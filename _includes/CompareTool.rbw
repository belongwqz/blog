#encoding:utf-8
$:.unshift File.join(File.dirname(__FILE__))
require 'wx'
require 'cmp_utils'
include Wx

#noinspection RubyArgCount,RubyResolve,RubyTooManyInstanceVariablesInspection
class SetDialog < Dialog
  def initialize
    super(nil, title: '设置', pos: [-1, -1], size: [350, 350], style: DEFAULT_DIALOG_STYLE)
    icon_file = File.join(File.dirname(__FILE__).to_s.encode('utf-8', 'gbk'), 'res.ico')
    set_icon(Icon.new(icon_file, BITMAP_TYPE_ICO)) if File.exist? icon_file
    @panel = Panel.new(self, pos: [0, 0], size: [350, 350])
    @file_filter_arr = Array.new
    @dir_filter_arr = Array.new
    @sep = "\n"

    StaticBox.new(@panel, label: '文件过滤', pos: [5, 7], size: [160, 260])
    @file_filter_ctrl = TextCtrl.new(
        @panel, pos: [10, 30], size: [150, 200],
        style: TE_MULTILINE|TE_PROCESS_ENTER)
    StaticText.new(@panel, label: "说明:以换行分割，且不能含\n中文，后缀匹配模式。", pos: [10, 233]).disable

    StaticBox.new(@panel, label: '目录过滤', pos: [180, 7], size: [160, 260])
    @dir_filter_ctrl = TextCtrl.new(
        @panel, pos: [185, 30], size: [150, 200],
        style: TE_MULTILINE|TE_PROCESS_ENTER)
    StaticText.new(@panel, label: "说明:以换行分割，且不能含\n中文，包含匹配模式。", pos: [185, 233]).disable

    Button.new(@panel, pos: [60, 280], label: '确定', id: ID_OK)
    Button.new(@panel, pos: [200, 280], label: '取消', id: ID_CANCEL)
  end

  def set_file_filter(arr)
    @file_filter_ctrl<<arr.join(@sep)
  end

  def set_dir_filter(arr)
    @dir_filter_ctrl<<arr.join(@sep)
  end

  def file_filter
    @file_filter_ctrl.get_value.chomp.strip.split(@sep)
  end

  def dir_filter
    @dir_filter_ctrl.get_value.chomp.strip.split(@sep)
  end
end

#noinspection RubyArgCount,RubyResolve,RubyTooManyInstanceVariablesInspection
class MainFrame < Frame
  def initialize
    super(nil, title: '升级配置比对工具', pos: [500, 300], size: [800, 600],
          style: (DEFAULT_FRAME_STYLE|STAY_ON_TOP|WS_EX_BLOCK_EVENTS) & ~(RESIZE_BORDER|RESIZE_BOX|MAXIMIZE_BOX))

    icon_file = File.join(File.dirname(__FILE__).to_s.encode('utf-8', 'gbk'), 'res.ico')
    set_icon(Icon.new(icon_file, BITMAP_TYPE_ICO)) if File.exist? icon_file
    @xpos = [5, 60, 360, 400, 530, 660]
    @ypos = [5, 35, 65, 95, 125, 155, 185]
    @dir_input_size = [300, 20]

    @src_dir = ''
    @des_dir = ''
    @third_dir = ''
    @def_data_file = ''
    @def_data = []
    @filter_file = ''
    @use_filter_bool = false
    @use_third_mode_bool = false
    @use_thread = false
    @use_def_data_bool = false
    @cfg = Cfg.new
    @cfg.read

    load_param
    @text_info = Queue.new
    @result_info = Array.new
    @start_run = false
    @start_time = nil
    @end_time = nil
    @show_group = true
    @right_file = 'fileProp.properties'

    @brow_btn_size = [30, -1]

    @panel = Panel.new(self)
    StaticText.new(@panel, label: '基础目录:', pos: [@xpos[0], @ypos[0]+4])
    @base_dir_val = TextCtrl.new(@panel, pos: [@xpos[1], @ypos[0]+2], size: @dir_input_size, value: @src_dir, style: TE_READONLY)
    Button.new(@panel, pos: [@xpos[2], @ypos[0]], size: @brow_btn_size, label: '浏览') do |btn_src|
      evt_button(btn_src.get_id) { |event| get_path(event, @base_dir_val) }
    end

    StaticText.new(@panel, label: '比对目录:', pos: [@xpos[0], @ypos[1]+4])
    @target_dir_val = TextCtrl.new(@panel, pos: [@xpos[1], @ypos[1]+2], size: @dir_input_size, value: @des_dir, style: TE_READONLY)
    Button.new(@panel, pos: [@xpos[2], @ypos[1]-2], size: @brow_btn_size, label: '浏览') do |btn_des|
      evt_button(btn_des.get_id) { |event| get_path(event, @target_dir_val) }
    end

    StaticText.new(@panel, label: '过滤文件:', pos: [@xpos[0], @ypos[2]+4])
    @filter_file_val = TextCtrl.new(@panel, pos: [@xpos[1], @ypos[2]+2], size: @dir_input_size, value: @filter_file, style: TE_READONLY)
    @filter_btn = Button.new(@panel, pos: [@xpos[2], @ypos[2]], size: @brow_btn_size, label: '浏览') do |btn_filter|
      evt_button(btn_filter.get_id) { |event| get_path(event, @filter_file_val, true) }
    end
    @filter_btn.enable false

    StaticText.new(@panel, label: '扩展目录:', pos: [@xpos[0], @ypos[3]+4])
    @third_dir_val = TextCtrl.new(@panel, pos: [@xpos[1], @ypos[3]+2], size: @dir_input_size, value: @third_dir, style: TE_READONLY)
    @third_dir_btn = Button.new(@panel, pos: [@xpos[2], @ypos[3]], size: @brow_btn_size, label: '浏览') do |btn_third|
      evt_button(btn_third.get_id) { |event| get_path(event, @third_dir_val, false) }
    end
    @third_dir_btn.enable false

    StaticText.new(@panel, label: '默认数据:', pos: [@xpos[0], @ypos[4]+4])
    @def_data_val = TextCtrl.new(@panel, pos: [@xpos[1], @ypos[4]+2], size: @dir_input_size, value: @def_data_file, style: TE_READONLY)
    @def_val_btn = Button.new(@panel, pos: [@xpos[2], @ypos[4]], size: @brow_btn_size, label: '浏览') do |btn_third|
      evt_button(btn_third.get_id) { |event| get_path(event, @def_data_val, true) }
    end
    @def_val_btn.enable false

=begin
    @threads = CheckBox.new(@panel, pos:[@xpos[3], @ypos[0]+4], label:'是否使用多线程')
    @threads.enable false
    @threads.set_value(@use_thread)
    evt_checkbox(@threads.get_id) do |_|
      @use_thread = @threads.get_value
      @cfg.set('use_thread', @use_thread)
    end
=end

    @use_filter = CheckBox.new(@panel, pos: [@xpos[3], @ypos[0]+4], label: '是否使用过滤文件')
    @use_filter.set_value(@use_filter_bool)
    evt_checkbox(@use_filter.get_id) do |v|
      unless v.is_checked
        @filter_file_val.set_value ''
      end
      @cfg.set('use_filter', @use_filter.get_value)
      @filter_btn.enable v.is_checked
    end

    @use_third_mode = CheckBox.new(@panel, pos: [@xpos[4], @ypos[0]+4], label: '是否使用扩展目录')
    @use_third_mode.set_value(@use_third_mode_bool)
    evt_checkbox(@use_third_mode.get_id) do |v|
      unless v.is_checked
        @third_dir_val.set_value ''
      end
      @cfg.set('use_third_mode', @use_third_mode.get_value)
      @third_dir_btn.enable v.is_checked
    end

    @use_def_data = CheckBox.new(@panel, pos: [@xpos[5], @ypos[0]+4], label: '是否使用默认数据')
    @use_def_data.set_value(@use_def_data_bool)
    evt_checkbox(@use_def_data.get_id) do |v|
      unless v.is_checked
        @def_data_val.set_value ''
        @def_data.clear
      end
      @cfg.set('use_def_data', @use_def_data.get_value)
      @def_val_btn.enable v.is_checked
    end

    Button.new(@panel, pos: [@xpos[3], @ypos[2]], label: '开始比较') do |btn_start|
      evt_button(btn_start.get_id) { |_| on_button }
    end

    @save_btn = Button.new(@panel, pos: [@xpos[4], @ypos[2]], label: '导出到excel') do |btn_start|
      evt_button(btn_start.get_id) { |_| save_to_excel }
    end
    @save_btn.enable false

    Button.new(@panel, pos: [@xpos[5], @ypos[2]], label: '过滤设置') do |btn_start|
      evt_button(btn_start.get_id) do |_|
        dlg = SetDialog.new
        dlg.set_file_filter($filter_file)
        dlg.set_dir_filter($filter_dir)
        case dlg.show_modal
          when ID_OK
            $filter_file = dlg.file_filter
            $filter_dir = dlg.dir_filter
            puts $filter_file
          when ID_CANCEL
            #$logger.info 'cancel'
          else
            #
        end
        dlg.destroy
      end
    end
    StaticText.new(@panel, label: %Q[说明:当使用扩展目录时，基础目录选升级前目录， \
比对目录选升级后目录，扩展目录选新安装目录，且必须指定过滤文件。使用默认数据将会对比对目录新增项进行过滤],
                   pos: [@xpos[3], @ypos[3]+4], size: [380, 50]).disable
    @text = TextCtrl.new(@panel, pos: [@xpos[0], @ypos[5]], style: TE_MULTILINE|SUNKEN_BORDER|TE_READONLY, size: [783, 415])

    evt_idle { idle_fun }
    evt_close { |event| @cfg.save; event.skip }
    show
  end

  def idle_fun
    if @use_thread
      until @text_info.empty?
        @text.append_text("#{@text_info.pop}")
      end
    end
  end

  def load_param
    begin
      @src_dir = File.absolute_path(@cfg.get('src_dir'))
      @des_dir = File.absolute_path(@cfg.get('des_dir'))
      #@use_thread = @cfg.get('use_thread')
      @use_filter_bool = @cfg.get('use_filter')
      @use_filter_bool = @use_filter_bool == 'NA' ? false : @use_filter_bool
      @use_third_mode_bool = @cfg.get('use_third_mode')
      @use_third_mode_bool = @use_third_mode_bool == 'NA' ? false : @use_third_mode_bool
      @use_def_data_bool = @cfg.get('use_def_data')
      @use_def_data_bool = @use_def_data_bool == 'NA' ? false : @use_def_data_bool
      @filter_file = @use_filter_bool ? File.absolute_path(@cfg.get('filter_file')) : ''
      @third_dir = @use_third_mode_bool ? File.absolute_path(@cfg.get('third_dir')) : ''
      @def_data_file = @use_def_data_bool ? File.absolute_path(@cfg.get('def_data_file')) : ''
    rescue
      $logger.info 'load_param error.'
    end
  end

  def save_to_excel
    @panel.enable false
    dlg = FileDialog.new(self, message: '保存结果到Excel文件', wildcard: 'Excel文件(*.xls)|*.xls||', style: FD_SAVE)
    if dlg.show_modal == ID_OK
      file_name = dlg.get_path
      if File.exist? file_name
        confirm = MessageDialog.new(self, caption: '请确认是否覆盖！', message: "#{dlg.get_filename}文件已经存在，是否进行覆盖？")
        unless confirm.show_modal == ID_OK
          return
        end
      end
      ext_info = [['基础目录', @base_dir_val.get_value],['比对目录', @target_dir_val.get_value],['扩展目录',@third_dir_val.get_value]]
      CmpUtils.export_to_excel(file_name, @result_info, @show_group, @right_file, @def_data, ext_info)
    end
    @panel.enable true
  end

  def get_path(_, ctrl, choose_file=false)
    if choose_file
      dlg = nil
      case ctrl
        when @def_data_val
          dlg = FileDialog.new(self, message: '选择默认数据配置文件', default_file: '', wildcard: '例外列表文件(*.xls;*.xlsx)|*.xls;*.xlsx||', style: FD_OPEN)
        when @filter_file_val
          dlg = FileDialog.new(self, message: '选择比对例外列表文件', default_file: 'ConfFileList.conf', wildcard: '例外列表文件(*.conf)|*.conf||', style: FD_OPEN)
        else
          #
      end
      if dlg.show_modal == ID_OK
        ctrl.set_value(File.absolute_path(dlg.get_path))
        @cfg.set('def_data_file', File.absolute_path(@def_data_val.get_value))
        @cfg.set('filter_file', File.absolute_path(@filter_file_val.get_value))
      end
    else
      dlg = DirDialog.new(self, message: '请选择目录', default_path: ctrl.get_value)
      if dlg.show_modal == ID_OK
        ctrl.set_value(File.absolute_path(dlg.get_path))
        @cfg.set('src_dir', File.absolute_path(@base_dir_val.get_value))
        @cfg.set('des_dir', File.absolute_path(@target_dir_val.get_value))
        @cfg.set('third_dir', File.absolute_path(@third_dir_val.get_value))
      end
    end
  end

  def message(msg)
    if @use_thread
      @text_info.push "#{msg}\n"
    else
      @text.append_text "#{msg}\n"
    end
  end

  def process(src, des)
    @cfg.save
    unless @start_run
      @start_run = true
      @start_time = Time.new
      message "#{'-'*120}@#{@start_time.to_s}"
      @filter_file = @filter_file_val.get_value
      filter_list = []
      filter_list = CmpUtils.read_filter @filter_file if @use_filter.is_checked && FileTest.exist?(@filter_file)
      @def_data_file = @def_data_val.get_value
      @def_data = CmpUtils.read_def_data @def_data_file if @use_def_data.is_checked && FileTest.exist?(@def_data_file)
      @result_info = DirCompare.new(src, des, filter_list, [], @right_file, @def_data, @third_dir_val.get_value).get_diff_info
      @end_time = Time.new
      message "耗时[#{(@end_time-@start_time).to_s}]秒"
      $logger.info "The task take[#{(@end_time-@start_time).to_s}] seconds."
      message "#{'-'*120}@#{@end_time.to_s}"
      message "比对细节请参见[#{$logger_file.to_s.encode('utf-8', 'gbk')}]。"
      @start_run = false
      @save_btn.enable true
    end
  end

  def on_button
    if @start_run
      message '上一次任务未完成，请稍后……'
    else
      @panel.enable false
      src = File.absolute_path @base_dir_val.get_value
      des = File.absolute_path @target_dir_val.get_value
      if Dir.exist?(src) && Dir.exist?(des) && src != des
        message '正在努力比对中，请耐心等待……(界面无响应属正常情况，比对完成后界面将自动恢复。)'
        if @use_thread
          Thread.start do
            process(src, des)
          end
        else
          process(src, des)
        end
      else
        message '参数错误！'
      end
      @panel.enable true
    end
  end
end

class MinimalApp < App
  def on_init
    MainFrame.new
  end
end

#noinspection RubyArgCount
if __FILE__ == $0
  if false
    src_xml = 'F:\version\9.3\diff\8.1-9.0\test_base\sfp.xml'
    des_xml = 'F:\version\9.3\diff\8.1-9.0\test_new\sfp.xml'
    puts SFPCmp.new(src_xml, des_xml).get_hashs.to_s
  else
    #noinspection RubyArgCount
    MinimalApp.new.main_loop
  end
end
