#encoding:utf-8
require 'writeexcel'
require 'rexml/document'
require 'hashdiff'
require 'logger'
require 'java_properties'
require 'active_support/all'
require 'pp'
require 'find'
require 'iniFile'
require 'fileutils'
require 'roo'
require 'spreadsheet'
require 'yaml'
include REXML
include JavaProperties
include Roo
$filter_dir = %w(.osgi .eclipse /samples/ /mdx_bak/ /MDXUpgrade/ conf_bak/ /baseline/)
$filter_file = %w(.sh .py .class .jar .tar .gz .xsd .ts .sql .vxml .bc .ts .mode .pid .active .standby Shutdown.properties .list .pid .syn .policy .jks)


class Logger
  # Creates or opens a secondary log file.
  def attach(name)
    @logdev.attach(name)
  end

  # Closes a secondary log file.
  def detach(name)
    @logdev.detach(name)
  end

  class LogDevice # :nodoc:
    attr_reader :devs

    def attach(log)
      @devs ||= {}
      @devs[log] = open_logfile(log)
    end

    def detach(log)
      @devs ||= {}
      @devs[log].close
      @devs.delete(log)
    end

    alias_method :old_write, :write

    def write(message)
      old_write(message)
      #$ch << message
      @devs ||= {}
      @devs.each do |_, dev|
        dev.write(message)
      end
    end
  end
end

$logger = Logger.new(STDOUT)
$logger_file = File.join(Dir.pwd, 'result.log')
$logger.attach($logger_file)

class BaseFile
  attr_accessor :hash
  attr_reader :file_obj
  attr_reader :file_path

  def initialize(file_name)
    @file_path = file_name
    @file_obj = File.new(@file_path)
    $logger.info "Open file [#{file_name}] to compare."
    @hash = Hash.new
  end

  def show_info
    @hash.each do |info|
      $logger.info info.to_s
    end
  end
end

class CommonXml < BaseFile
  def initialize(file_name)
    super(file_name)
    begin
      @hash = Hash.from_xml(@file_obj)
    rescue => err
      $logger.error "load file [#{file_name}] fail cause [#{err.to_s}]."
    end
  end
end

class MML < BaseFile
  def initialize(file_name)
    super(file_name)
    Document.new(@file_obj).root.each_element do |element|
      begin
        @hash[element.attribute('name').to_s]=element.attribute('value').to_s
      rescue => err
        $logger.error "load file [#{file_name}] fail cause [#{err.to_s}]."
      end
    end
  end
end

class SFPCmp < Object
  attr_reader :hash_src
  attr_reader :hash_des

  def initialize(file_src, file_des)
    src_arr = read(file_src)
    des_arr = read(file_des)
    src_res = src_arr - des_arr
    des_res = des_arr - src_arr
    @hash_src = Hash.new
    @hash_des = Hash.new
    unless src_res.empty? || des_res.empty?
      @hash_src[src_res[0][0]] = "#{src_res[0][1][0]}_#{src_res[0][1][1]}"
      @hash_des[des_res[0][0]] = "#{des_res[0][1][0]}_#{des_res[0][1][1]}"
    end
  end

  def get_hashs
    [@hash_src, @hash_des]
  end

  def read(file_path)
    hash_tmp = []
    Document.new(File.open(file_path)).root.each_element do |ele|
      hash_tmp.push [ele.elements['sfp_id'].text, [ele.elements['sfp_status'].text, ele.elements['sfp_value'].text]]
    end
    hash_tmp
  end
end

class Property < BaseFile
  #noinspection RubyResolve
  def initialize(file_name)
    super(file_name)
    begin
      Properties.load(@file_obj).each do |info|
        @hash[info[0].to_s]=info[1].to_s
      end
    rescue => err
      $logger.error "load file [#{file_name}] fail cause [#{err.to_s}]."
    end
  end
end

class Ini < BaseFile
  #noinspection RubyResolve
  def initialize(file_name)
    super(file_name)
    begin
      @hash = IniFile.load(@file_obj).to_h
    rescue => err
      $logger.info "load file [#{file_name}] in ini format fail cause [#{err.to_s}], try to load as properties file now."
      begin
        @hash = Property.new(file_name).hash
      rescue => errAgain
        $logger.error "load file [#{file_name}] as properties fail cause [#{errAgain.to_s}]."
      end
    end
  end
end

class HashCompare
  attr_accessor :diff_info

  def initialize(src_hash, des_hash)
    @diff_info = HashDiff.best_diff(src_hash, des_hash)
  end

  def show_info
    @diff_info
  end
end

class FileDiffInfo
  attr_reader :file_name
  attr_reader :file_flag
  attr_reader :info
  attr_reader :diff_info
  attr_reader :file_bin_same
  attr_reader :third_mode

  def initialize(name, flag, third=false)
    @file_name = name
    @file_flag = flag
    @diff_info = []
    @file_bin_same = false
    @third_mode = third
    case flag
      when '='
        @info = '变更'
      when '-'
        @info = '删除'
      when '+'
        @info = '新增'
      when '!'
        @info = '比对工具不支持，需要手工比较'
      else
        @info = '错误'
    end
  end

  def bin_same(be_same)
    @file_bin_same = be_same
    @info = @file_bin_same ? '二进制相同' : '二进制不同'
  end

  def add_diff_info(info)
    if @file_flag == '='
      @diff_info.push info
    else
      $logger.warn("call add_diff_info error cause type is [#{@file_flag}]")
    end
  end
end

# noinspection RubyTooManyInstanceVariablesInspection
class DirCompare
  attr_accessor :diff_info

  def initialize(src_dir, des_dir, filter_keys=[], filter_types=[], right_file='fileProp.properties', def_data=[], third_dir='')
    @src_dir_name = src_dir
    @des_dir_name = des_dir
    @right_file = right_file
    @def_data = def_data
    @third_dir_name = third_dir

    @filter_keys = $filter_dir
    @filter_conf_list = filter_keys
    @filter_keys.concat filter_keys

    @filter_types = $filter_file
    @filter_types.concat filter_types

    $logger.info "Find files in dir[#{@src_dir_name}], wait……"
    @src_files = Find.find(@src_dir_name).to_a.delete_if { |f| filter_file f }
    $logger.info "Find files in dir[#{@src_dir_name}], finish."

    $logger.info "Find files in dir[#{@des_dir_name}], wait……"
    @des_files = Find.find(@des_dir_name).to_a.delete_if { |f| filter_file f }
    $logger.info "Find files in dir[#{@des_dir_name}], finish"

    $logger.info "filter file type list is #{@filter_types.to_s}"
    $logger.info "filter key list is #{@filter_keys.to_s}"

    @diff_info = Array.new
  end

  def is_def_data(file_name, diff)
    @def_data.each { |data| return true if file_name == data[:file] and diff[0] == '+' and data[:key] == diff[1] and data[:value] == diff[2] }
    false
  end

  def get_file_diff_info(src_file, des_file, use_third=false)
    res = nil
    if src_file.to_s.ends_with? @right_file
      $logger.info "file content diff not show right file [#{src_file}]"
    else
      $logger.info "[#{src_file}]<=>[#{des_file}] begin"
      case File.extname(src_file).downcase
        when '.xml'
          res = get_xml_diff_info(src_file, des_file, use_third)
        when '.properties'
          res = get_properties_diff_info(src_file, des_file, use_third)
        when '.ini'
          res = get_ini_diff_info(src_file, des_file, use_third)
        else
          res = get_bin_diff_info(src_file, des_file, use_third)
      end
      #$logger.info "before #{res.to_s}"
      #使用默认数据进行过滤
      res.diff_info.reject! { |diff| is_def_data(File.basename(res.file_name), diff) } unless res.nil?
      #$logger.info "after #{res.to_s}"
      $logger.info "[#{src_file}]<=>[#{des_file}] end"
    end
    res
  end

  def get_third_diff_info
    third_diff_infos = Array.new
    $logger.info 'third_diff_infos begin make.'
    if FileTest.exist? @third_dir_name and not @filter_conf_list.empty?
      @filter_conf_list.each do |fn|
        src_file = "#{@des_dir_name}#{fn}"
        des_file = "#{@third_dir_name}#{fn}"
        if FileTest.exist? src_file and FileTest.exist? des_file
          $logger.info "find [#{fn}] at [#{src_file}]."
          res = get_file_diff_info(src_file, des_file, true)
          $logger.info "result is [#{res.to_s}]."
          third_diff_infos.push res
        else
          src_file = "#{@des_dir_name}/media1#{fn}"
          des_file = "#{@third_dir_name}/media1#{fn}"
          if FileTest.exist? src_file and FileTest.exist? des_file
            $logger.info "find [#{fn}] at [#{src_file}]."
            res = get_file_diff_info(src_file, des_file, true)
            $logger.info "result is [#{res.to_s}]."
            third_diff_infos.push res
          else
            $logger.info "can not find [#{fn}] at media1."
          end
          src_file = "#{@des_dir_name}/media2#{fn}"
          des_file = "#{@third_dir_name}/media2#{fn}"
          if FileTest.exist? src_file and FileTest.exist? des_file
            $logger.info "find [#{fn}] at [#{src_file}]."
            res = get_file_diff_info(src_file, des_file, true)
            $logger.info "result is [#{res.to_s}]."
            third_diff_infos.push res
          else
            $logger.info "can not find [#{fn}]  at media2."
          end
        end
      end
    end
    third_diff_infos.compact!
    $logger.info "third_diff_infos is [#{third_diff_infos.to_s}]."
    third_diff_infos
  end

  #获取差异信息
  def get_diff_info
    diff_infos = Array.new
    $logger.info "Compare dir between [#{@src_dir_name}] and [#{@des_dir_name}] begin"
    calc_result = calc(@src_files, @des_files)
    total_count = calc_result.size
    proc_count = 0
    calc_result.each do |info|
      proc_count += 1
      $logger.info "process #{format('%0.2f',proc_count/total_count.to_f * 100)}%, total_count=#{total_count}, proc_count=#{proc_count}"
      case info[0]
        when '='
          res = get_file_diff_info(info[1], info[2])
          diff_infos.push res unless res.nil?
        when '-'
          src_file = info[1]
          diff_infos.push FileDiffInfo.new(src_file[@src_dir_name.size, src_file.size-@src_dir_name.size], '-')
          $logger.info info.to_s
        when '+'
          des_file = info[1]
          diff_infos.push FileDiffInfo.new(des_file[@des_dir_name.size, des_file.size-@des_dir_name.size], '+')
          $logger.info info.to_s
        else
          $logger.info 'error'
      end
    end

    $logger.info "Compare dir between [#{@src_dir_name}] and [#{@des_dir_name}] end"
    third_diff_info = get_third_diff_info
    diff_infos.concat third_diff_info unless third_diff_info.empty?
    diff_infos
  end

  private
  def calc(src_files_array, des_files_array)
    if @diff_info.empty?
      $logger.info 'Begin to compare dir, wait……'
      src_files_array.each do |src_file|
        (des_files_array.each.include?(src_file.sub(@src_dir_name, @des_dir_name))) ?
            @diff_info.push(['=', src_file, src_file.sub(@src_dir_name, @des_dir_name)]) :
            @diff_info.push(['-', src_file])
      end
      des_files_array.each do |des_file|
        @diff_info.push(['+', des_file]) unless src_files_array.each.include?(des_file.sub(@des_dir_name, @src_dir_name))
      end
      $logger.info 'Begin to compare dir, finish'
    end
    @diff_info
  end

  #文件过滤，返回true表示不需要比对，false表示需要比对
  def filter_file(file_name)
    #删除文件夹，不做文件夹名的比较
    if File.directory?(file_name)
      $logger.info "skip dir [#{file_name}]"
      return true
    end

    #根据关键字过滤，如果包含关键字则被过滤
    if @filter_keys.any? do |k|
      if file_name.to_s.include? k
        $logger.info "use filter key [#{k}] to skip file [#{file_name}]"
        true
      end
    end
      return true
    end

    #根据文件类型过滤，如果后缀匹配上则被过滤
    if @filter_types.any? do |k|
      if file_name.to_s.ends_with? k
        $logger.info "use filter type [#{k}] to skip file [#{file_name}]"
        true
      end
    end
      return true
    end

    false
  end

  def get_show_name(full_name, use_third=false)
    use_third ?
        full_name[@third_dir_name.size, full_name.size-@third_dir_name.size] :
        full_name[@des_dir_name.size, full_name.size-@des_dir_name.size]
  end

  #获取xml差异信息
  def get_xml_diff_info(src_xml, des_xml, use_third=false)
    file_name = File.basename(src_xml)
    xml_diff = FileDiffInfo.new(get_show_name(des_xml, use_third), '=', use_third)
    use_bin_mode = false
    case file_name
      when 'cluster-common-conf.xml'
        HashCompare.new(MML.new(src_xml).hash, MML.new(des_xml).hash).show_info.each do |arr|
          xml_diff.add_diff_info arr
          $logger.info arr.to_s
        end
      when 'sfp.xml'
        HashCompare.new(*SFPCmp.new(src_xml, des_xml).get_hashs).show_info.each do |arr|
          xml_diff.add_diff_info arr
          $logger.info arr.to_s
        end
      when 'global-conf.xml', 'flowControl.xml'
        use_bin_mode = true
        xml_diff = get_bin_diff_info(src_xml, des_xml, use_third)
        #这几个文件较复杂，直接使用二进制方式比较
        $logger.info "[#{file_name}] use bin diff!"
      else
        HashCompare.new(CommonXml.new(src_xml).hash, CommonXml.new(des_xml).hash).show_info.each do |arr|
          xml_diff.add_diff_info arr
          $logger.info arr.to_s
        end
    end
    (xml_diff = nil if xml_diff.diff_info.empty?) unless use_bin_mode
    xml_diff
  end

  #获取properties文件比对信息
  def get_properties_diff_info(src_pro, des_pro, use_third=false)
    pro_diff = FileDiffInfo.new(get_show_name(des_pro, use_third), '=', use_third)
    HashCompare.new(Property.new(src_pro).hash, Property.new(des_pro).hash).show_info.each do |arr|
      if src_pro.to_s.ends_with?(@right_file) && src_pro.to_s.ends_with?(@right_file)
        unless arr.any? { |ele| filter_file(ele) }
          pro_diff.add_diff_info(arr)
          $logger.info arr.to_s
        end
      else
        pro_diff.add_diff_info(arr)
        $logger.info arr.to_s
      end
    end
    pro_diff = nil if pro_diff.diff_info.empty?
    pro_diff
  end

  #获取ini文件比对信息
  def get_ini_diff_info(src_ini, des_ini, use_third=false)
    ini_diff = FileDiffInfo.new(get_show_name(des_ini, use_third), '=', use_third)
    HashCompare.new(Ini.new(src_ini).hash, Ini.new(des_ini).hash).show_info.each do |arr|
      ini_diff.add_diff_info arr
      $logger.info arr.to_s
    end
    ini_diff = nil if ini_diff.diff_info.empty?
    ini_diff
  end

  #获取二进制文件比对信息
  def get_bin_diff_info(src_bin, des_bin, use_third=false)
    bin_diff = FileDiffInfo.new(get_show_name(des_bin, use_third), '!', use_third)
    bin_diff.bin_same FileUtils.compare_file(src_bin.to_s.force_encoding('utf-8'), des_bin.to_s.force_encoding('utf-8'))
    $logger.info "[#{File.basename(src_bin).to_s}] cmp in binary mode, they are #{bin_diff.file_bin_same ? 'same' : 'not same'}"
    bin_diff = nil if bin_diff.file_bin_same
    bin_diff
  end
end

# noinspection RubyResolve
class Cfg
  attr_accessor :param_map, :file_cfg

  def initialize
    @param_map=Hash.new
    @file_cfg = 'c:\\cfg.yml'
  end

  def read
    open(@file_cfg) { |f| @param_map = YAML.load(f) } if File.exist? @file_cfg
    #防止文件读取失败造成的异常
    if @param_map.class.name != 'Hash'
      @param_map = Hash.new
    end
  end

  def save
    open(@file_cfg, 'w') { |f| YAML.dump(@param_map, f) }
  end

  def set(key, val)
    @param_map[key] = val
  end

  def get(key)
    @param_map.has_key?(key) ? @param_map[key] : 'NA'
  end
end

#noinspection RubyClassVariableUsageInspection
class CmpUtils
  @@group_has = %w(/opt/MediaX3600/iom/
        /opt/MediaX3600/nodeagent/
        /opt/MediaX3600/vcs-nodeagent/
        /opt/MediaX3600/mdu/
        /opt/MediaX3600/mediax/business/conf/mdxgu/
        /opt/MediaX3600/mediax/business/conf/sipdpu/
        /opt/MediaX3600/mediax/business/conf/soapdpu
        /opt/MediaX3600/mediax/business/conf/mdxdu/
        /opt/MediaX3600/mediax/business/conf/mdxhu/
        /opt/MediaX3600/mediax/tools/
        /opt/MediaX3600/mediax/commonconf/
        /opt/MediaX3600/mediax/mdxdb/
        /etc
    )
  @@group_hot = %w(
      /opt/MediaX3600/mediax/business/
      cluster/cluster-common-conf.xml
      conf/table/data/sfp.xml
      mediax/commonconf/sfp.properties
      data/mrs.xml
    )
  @@group_mft = %w(
      /opt/MediaX3600/mediax/uecontrolportal/
      /opt/MediaX3600/mediax/webresource/
      /opt/MediaX3600/mediax/userportal/
    )

  def self.read_filter(file_name, pre_fix='/opt/MediaX3600/')
    filter_list = []
    if FileTest.exist?(file_name)
      File.open(file_name).each do |line|
        filter_list.push pre_fix + line.chomp
        filter_list.delete(pre_fix)
      end
    end
    filter_list
  end

  def self.get_group(path_name)
    group_name = 'NA'
    if @@group_has.any? { |key_info| path_name.to_s.include?(key_info) &&
        path_name.to_s.exclude?('cluster-common-conf.xml') &&
        path_name.to_s.exclude?('sfp.xml') &&
        path_name.to_s.exclude?('sfp.properties') &&
        path_name.to_s.exclude?('mrs.xml')
    }
      group_name = 'HAS'
    elsif @@group_hot.any? { |key_info| path_name.to_s.include? key_info }
      group_name = 'HOT'
    elsif @@group_mft.any? { |key_info| path_name.to_s.include? key_info }
      group_name = 'MFT'
    end
    group_name
  end

  def self.read_def_data(file_name, cfg_name_col=1, data_key_col=2, key_val_col=3)
    result = Array.new
    skip_row_count = 1

    case File.extname(file_name).downcase
      when '.xls'
        s = Excel.new(file_name)
      when '.xlsx'
        s = Excelx.new(file_name)
      else
        return result
    end

    unless s.nil?
      s.default_sheet = s.sheets.first
      (s.first_row+skip_row_count).upto(s.last_row) do |row|
        result.append({:file => s.cell(row, cfg_name_col).to_s, :key => s.cell(row, data_key_col).to_s,
                       :value => s.cell(row, key_val_col).to_s})
      end
    end
    result
  end

  def self.try_utf8(cont)
    if cont.nil?
      return ''
    end
    result = ''
    begin
      result = cont.to_s.encode('utf-8', :replace => '?')
      unless result.valid_encoding?
        result = cont.to_s.force_encoding('utf-8')
      end
      unless result.valid_encoding?
        result = cont.to_s.encode('utf-8', 'gbk', :replace => '?')
      end
      unless result.valid_encoding?
        result = info.to_s
      end
    rescue => err
      $logger.info "#{cont.to_s.encoding}:#{cont.to_s.valid_encoding?}:#{cont}:#{err.to_s}"
      result = info.to_s
    end
    return result
  end

  def self.export_to_excel(full_path, result_info, show_group=true, right_file='fileProp.properties', def_data=[], ext_info=[])
    begin
      workbook = WriteExcel.new(full_path)
      format = workbook.add_format(:border => 2)
      default_sheet= workbook.add_worksheet '说明'
      ext_info.each_with_index do |info_arr, i|
        info_arr.each_with_index do |info, j|
          default_sheet.write(i, j, info, format)
        end
      end
      #format_merge = workbook.add_format(:border=>1, :bold=>1, :color=>'blue', :align=>'left', :valign=>'vcenter')
      file_diff_sheet= workbook.add_worksheet '文件变更'
      file_diff_row_index = 0
      file_diff_sheet.write(file_diff_row_index, 0, '文件名', format)
      file_diff_sheet.write(file_diff_row_index, 1, '变更类型', format)
      if show_group
        file_diff_sheet.write(file_diff_row_index, 2, '项目组', format)
      end
      file_diff_row_index += 1

      file_cont_diff_sheet = workbook.add_worksheet '文件内容修改'
      file_cont_diff_row_index = 0
      file_cont_diff_sheet.write(file_cont_diff_row_index, 0, '文件名', format)
      file_cont_diff_sheet.write(file_cont_diff_row_index, 1, '变更项', format)
      file_cont_diff_sheet.write(file_cont_diff_row_index, 2, '基础值', format)
      file_cont_diff_sheet.write(file_cont_diff_row_index, 3, '变化值', format)
      if show_group
        file_cont_diff_sheet.write(file_cont_diff_row_index, 4, '项目组', format)
      end
      file_cont_diff_row_index += 1

      file_cont_add_diff_sheet = workbook.add_worksheet '文件内容新增'
      file_cont_add_diff_row_index = 0
      file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 0, '文件名', format)
      file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 1, '新增项', format)
      file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 2, '新增值', format)
      if show_group
        file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 3, '项目组', format)
      end
      file_cont_add_diff_row_index += 1

      file_cont_rm_diff_sheet = workbook.add_worksheet '文件内容删除'
      file_cont_rm_diff_row_index = 0
      file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 0, '文件名', format)
      file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 1, '删除项', format)
      file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 2, '删除值', format)
      if show_group
        file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 3, '项目组', format)
      end
      file_cont_rm_diff_row_index += 1

      result_info.each do |info|
        case info.file_flag
          when '='
            unless info.diff_info.empty?
              info.diff_info.each do |detail|
                #print info.file_name
                #print detail.to_s
                case detail[0]
                  when '+'
                    file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 0, info.file_name.to_s, format)
                    file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 1, detail[1].to_s, format)
                    file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 2, detail[2].to_s, format)
                    if show_group
                      if info.file_name.to_s.ends_with? right_file
                        file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 3, get_group(detail[1].to_s), format)
                      else
                        file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 3, get_group(info.file_name), format)
                      end
                    end
                    if info.third_mode
                      file_cont_add_diff_sheet.write(file_cont_add_diff_row_index, 4, '扩展', format)
                    end
                    file_cont_add_diff_row_index += 1
                  when '-'
                    file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 0, info.file_name.to_s, format)
                    file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 1, detail[1].to_s, format)
                    file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 2, detail[2].to_s, format)
                    if show_group
                      if info.file_name.to_s.ends_with? right_file
                        file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 3, get_group(detail[1].to_s), format)
                      else
                        file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 3, get_group(info.file_name), format)
                      end
                    end
                    if info.third_mode
                      file_cont_rm_diff_sheet.write(file_cont_rm_diff_row_index, 4, '扩展', format)
                    end
                    file_cont_rm_diff_row_index += 1
                  when '~'
                    file_cont_diff_sheet.write(file_cont_diff_row_index, 0, info.file_name.to_s, format)
                    file_cont_diff_sheet.write(file_cont_diff_row_index, 1, detail[1].to_s, format)
                    file_cont_diff_sheet.write(file_cont_diff_row_index, 2, try_utf8(detail[2]), format)
                    file_cont_diff_sheet.write(file_cont_diff_row_index, 3, try_utf8(detail[3]), format)
                    if show_group
                      if info.file_name.to_s.ends_with? right_file
                        file_cont_diff_sheet.write(file_cont_diff_row_index, 4, get_group(detail[1].to_s), format)
                      else
                        file_cont_diff_sheet.write(file_cont_diff_row_index, 4, get_group(info.file_name), format)
                      end
                    end
                    if info.third_mode
                      file_cont_diff_sheet.write(file_cont_diff_row_index, 5, '扩展', format)
                    end
                    file_cont_diff_row_index += 1
                  else
                    puts 'should not be here'
                end
              end
            end
          when '-', '+'
            file_diff_sheet.write(file_diff_row_index, 0, info.file_name.to_s, format)
            file_diff_sheet.write(file_diff_row_index, 1, info.info.to_s, format)
            if show_group
              file_diff_sheet.write(file_diff_row_index, 2, get_group(info.file_name), format)
            end
            if info.third_mode
              file_diff_sheet.write(file_diff_row_index, 3, '扩展', format)
            end
            file_diff_row_index += 1
          when '!'
            file_diff_sheet.write(file_diff_row_index, 0, info.file_name.to_s, format)
            file_diff_sheet.write(file_diff_row_index, 1, info.info.to_s, format)
            if show_group
              file_diff_sheet.write(file_diff_row_index, 2, get_group(info.file_name), format)
            end
            if info.third_mode
              file_diff_sheet.write(file_diff_row_index, 3, '扩展', format)
            end
            file_diff_row_index += 1
          else
        end
      end
      unless def_data.empty?
        def_data_sheet = workbook.add_worksheet '默认数据'
        def_data_row_index = 0
        def_data_sheet.write(def_data_row_index, 0, '文件名', format)
        def_data_sheet.write(def_data_row_index, 1, '参数名', format)
        def_data_sheet.write(def_data_row_index, 2, '参数值', format)
        def_data.each do |info|
          def_data_row_index += 1
          def_data_sheet.write(def_data_row_index, 0, info[:file], format)
          def_data_sheet.write(def_data_row_index, 1, info[:key], format)
          def_data_sheet.write(def_data_row_index, 2, info[:value], format)
        end
      end
      workbook.close
      true
    rescue => err
      puts err
      false
    end
  end
end
