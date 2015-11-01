---
layout: post
title: rails 兴趣教程
description: 任何东西的的学习基本上都是先有兴趣，然后瓶颈，突破了之后再瓶颈，再去突破的过程，这里介绍一些用于提升rails入门兴趣的东东，希望对有心之人有帮助。

---


# 1. 汇总gem文件 #

*-gemfile添加：*

    gem "rails-i18n"
    gem "devise"
    gem "devise-i18n"
    gem "cancancan"
    gem "rolify"
    gem "rails_admin"
    gem "rails_admin-i18n"
    gem "rails_kindeditor"
    gem "twitter-bootstrap-rails"
    gem "twitter-bootswatch-rails"
    gem "twitter-bootswatch-rails-helpers
    
    bootswatch在windows下依赖v8，麻烦多，可不用
    gem "simple_form"
    gem "slim-rails"
    gem "sidekiq" 需要单独安装redis
    gem 'coffee-script-source', '1.8.0'
    规避1.9版本在windowns下的bug

# 2. 安装 #

    gem update --system
    rails update --no-ri --no-rdoc
    gem install rails --no-ri --no-rdoc
    for %i in (
    rails-i18n
    sqlite3
    turbolinks
    tzinfo-data
    uglifier
    web-console
    devise
    devise-i18n
    cancancan
    rolify
    rails_admin
    rails_admin-i18n
    rails_kindeditor
    twitter-bootstrap-rails
    twitter-bootswatch-rails
    twitter-bootswatch-rails-helpers
    simple_form
    slim-rails
    sidekiq
    ) do (
    gem install %i --no-ri --no-rdoc
    )
    
    rails new om

# 3. 手工补充 #

*application.rb增加：*

    config.generators do |g|
      g.template_engine :slim
    end
    config.i18n.load_path += Dir[Rails.root.join('config', 'locales', '**', '*.{rb,yml}').to_s]
    config.i18n.default_locale = :'zh-CN'

*增加文件：zh-CN.yml*

    样例见后面

*模型设计：*

    system {
    name  系统名
    short 英文缩写
    env 环境类型（开发、测试、生产）
    desc:text
    }
    rails g scaffold system name short env desc:text
    rake db:migrate RAILS_ENV=development

*修改route：*

    root 'systems#index'

# 4. 启动 #

    rails g simple_form:install --bootstrap
    rails g bootstrap:install static --no-coffeescript
    rails g bootstrap:themed systems -f
    rails g devise:install
    rails g devise User
    rails g devise:views
    rails g cancan:ability
    rails g rolify Role User
    rails g rails_admin:install
    rake db:migrate RAILS_ENV=development
    rails s

# 5. 富文本编辑器kindeditor #
    
    在需要rich edit的地方加上", :as => :kindeditor", 
    在跳转到form可能用到rich edit的地方加上（一般index和show的new和edit需要加）, 如：
    link_to t('.edit', :default => t("helpers.links.edit")), edit_system_path(system), :class => 'btn btn-default btn-xs', 'data-no-turbolink' => true
    'data-no-turbolink' => true或者:'data-no-turbolink' => true都可以，如果带有符号的需要加单引号

# 6. 登录 #

*application_controller.rb增加：*

    before_action :authenticate_user!
    
    def after_sign_in_path_for(resource)
      if resource.is_a?(User)
        if User.count == 1
          resource.add_role 'admin'
        end
        resource
      end
      root_path
    end

*application.html.erb增加：*

    <% if current_user %>
      <%= current_user.email %> |
      <%= link_to('退出', destroy_user_session_path, :method => :delete) %> |
      <%= link_to('修改密码', edit_registration_path(:user)) %>
    <% else %>
      <%= link_to('注册', new_registration_path(:user)) %> |
      <%= link_to('登录', new_session_path(:user)) %>
    <% end %><span></span>
    <p class="notice"><%= notice %></p>  <p class="alert"><%= alert %></p>

*xxcontroller.rb增加：*

    load_and_authorize_resource

*index.html.slim和show.html.slim修改：*

    - if can? :update, System
      = link_to t('.edit'xxx
    
    - if can? :destroy, System
      = link_to t('.destroy'xxx
    
    - if can? :create, System
      = link_to t('.new'xxx

*ability.rb修改（可自定义）：*

    can :read, :all
    if user.has_role? :admin
      can :access, :rails_admin
      can :dashboard
      can :manage, :all
    else
       can :read, :all
    end

*rails_admin.rb添加：*

    config.authorize_with do
      redirect_to '/' unless current_user.has_role? :admin
    end

*在application_controller.rb增加如下函数*

    def set_locale 
      I18n.locale = params[:locale] || I18n.default_locale 
    end 
    然后在before_action里调用


# 7. 富文本编辑器的另外一个选择 #

    gem 'ckeditor'
    gem 'paperclip'
    rails g ckeditor:install --orm=active_record --backend=paperclip
    
    gem 'carrierwave'
    gem 'mini_magick'
    rails g ckeditor:install --orm=active_record --backend=carrierwave
    
    gem 'dragonfly'
    rails g ckeditor:install --orm=active_record --backend=dragonfly
    
    gem 'mongoid-paperclip', :require => 'mongoid_paperclip'
    rails g ckeditor:install --orm=mongoid --backend=paperclip
    
    gem 'carrierwave-mongoid', :require => 'carrierwave/mongoid'
    gem 'mini_magick'
    rails g ckeditor:install --orm=mongoid --backend=carrierwave

*application.rb添加:*

    config.autoload_paths += %W(#{config.root}/app/models/ckeditor)

*config/routes.rb添加:*

    mount Ckeditor::Engine => '/ckeditor'

*app/assets/javascripts/application.js添加:*

    //= require ckeditor/init

*config/initializers/assets.rb添加:*

    Rails.application.config.assets.precompile += %w( ckeditor/* )

*Form helpers:*

    <%= form_for @page do |form| -%>
      <%= form.cktext_area :notes, :class => 'someclass',
        :ckeditor => {:language => 'uk'} %>
      <%= form.cktext_area :content, :value => 'Default value',
        :id => 'sometext' %>
      <%= cktext_area :page, :info, :cols => 40,
        :ckeditor => {:uiColor => '#AADC6E', :toolbar => 'mini'} %>
    <% end -%>
    
# 8. 其他插件 #

    gem 'formtastic'
    rails g formtastic:install

# 9.zh-CN.yml样例 #

    zh-CN:
      hello: "Hello world"
      activerecord:
        models:
          system:
            one: '系统'
            other: '系统'
          user:
            one: '用户'
            other: '用户'
          role:
            one: '角色'
            other: '角色'
        attributes:
          system:
            id: '系统ID'
            name: '系统名'
            short: '英文缩写'
            env: '环境类型'
            desc: '系统信息'
            created_at: '系统录入时间'
            updated_at: '系统更新时间'
          user:
            id: '用户ID'
            email: '邮箱'
            reset_password_sent_at: '重置密码送时间'
            remember_created_at: '记住密码创建时间'
            sign_in_count: '登陆数'
            current_sign_in_at: '当前登陆时间'
            last_sign_in_at: '上次登陆时间'
            current_sign_in_ip: '当前登录IP'
            last_sign_in_ip: '上次登陆IP'
            created_at: '创建时间'
            updated_at: '修改时间'
            roles: '所属角色'
            password: '密码'
            password_confirmation: '密码确认'
            reset_password_token: '密码重置Token'
          role:
            id: '角色ID'
            name: '角色名'
            created_at: '创建时间'
            updated_at: '更新时间'
            users: '用户列表'
      helpers:
        actions: '操作'
        titles:
          edit: '编辑%{model}'
          new: '新增%{model}'
          destroy: '删除%{model}'
        links:
          new: '新增'
          edit: '编辑'
          confirm: '是否确认？'
          destroy: '删除'
          cancel: '取消'
          back: '返回'
      admin:
        js: 'js脚本'
        loading: '加载中'
        toggle_navigation: '切换导航'
        export:
    
          select_all_fields: '选择所有字段'
