---
layout: post
title: rails 兴趣教程
description: 任何东西的的学习基本上都是先有兴趣，然后瓶颈，突破了之后再瓶颈，再去突破的过程，这里介绍一些用于提升rails入门兴趣的东东，希望对有心之人有帮助。

---


# 1. 汇总gem文件 #

*-gemfile添加：*

    gem 'twitter-bootstrap-rails'
    gem 'cancan'
    gem 'devise'
    gem 'devise-i18n'
    gem 'rails_kindeditor'
    gem 'rails_admin'
    gem 'rails_admin-i18n'
    gem 'rails-i18n'
    bundle install

# 2. 自动生成相应代码 #

    rails g scaffold Article title:string content:text
    rails g model Comment commenter:string body:text article:references
    rails g bootstrap:install static --no-coffeescript
    rails g bootstrap:themed articles -f #后面这个articles是controller的名字
    rails g rails_kindeditor:install
    rails g devise:install
    rails g devise User
    rails g devise:views
    rails g rails_admin:install
    rails g cancan:ability

# 3. 手工补充 #

*-model Article 添加：*

    has_many :comments, dependent: :destroy

*-controller添加：*

    before_action :authenticate_user!

*-route.rb 添加：*

    root 'articles#index'
*-config/environments/development.rb添加:*

    config.action_mailer.default_url_options = { host: 'localhost', port: 3000 }

*-config/application.rb添加:*

    config.i18n.default_locale = 'zh-CN'
*将语言文件拷贝到locales目录*

*-articles的_form.html.erb变更：*

    <%= f.text_field :content, :class => 'form-control' %>
改为

    <%= f.kindeditor :content, :class => 'form-control' %>

所有跳到需要kindeditor的link添加'data-no-turbolink' => true属性

*-application_controller.rb合适的地方添加：*

    <%=notice%><%=alert%>
    <% if user_signed_in? %>
      <%= current_user.email %>&nbsp;
      <%= link_to '注销', destroy_user_session_path,
        :class => 'navbar-link', :method => :delete %>
    <% else %>
      <%= link_to '注册', new_user_registration_path, :class => 'navbar-link' %>|
      <%= link_to '登录', new_user_session_path, :class => 'navbar-link' %>
    <% end %>

*comments和Article的关联页面这里不给出，自行实现。*

# 4. 启动 #

    rake db:migrate
    rails s

# 5. 富文本编辑器的另外一个选择 #

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

# 1. 其他插件 #

    gem 'formtastic'
    rails g formtastic:install
