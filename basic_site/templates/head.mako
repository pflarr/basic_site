<HTML>
<HEAD>
    <TITLE>${request.registry.settings['site_name'] + page_subtitle|h}</TITLE>
    <LINK type="text/css" rel="stylesheet"
          href="${request.static_url('basic_site:static/base.css')}">
    <LINK type="text/css" rel="stylesheet"
          href="${request.route_url('file', name='theme.css')}">
    <LINK type="text/css" rel="stylesheet"
          href="${request.route_url('file', name='site.css')}">
</HEAD>
<DIV class="login">
  % if user == None:
      <FORM action='' method="POST">
        <LABEL target="user">User</LABEL>
        <INPUT type="text" size=10 name="user"> 
        <LABEL target="passwd">Password</LABEL>
        <INPUT type="password" size=10 name="passwd">
        <BUTTON type="submit">Login</BUTTON>
      </FORM>
  % else:
      Logged in as <STRONG>${user.uid}</STRONG> 
      (<A href="${request.route_url('logout')}">logout</A>)
  % endif
</DIV>

<DIV class="head">
    <IMG src="${request.route_url('file',name='logo.png')}">
</DIV>

% if msg:
  % for item in msg:
    <DIV class="message">${item|h}</DIV>
  % endfor
% endif

<%
    def cur_class(this_page):
        if this_page == page_name:
            return 'class="current"'
        else:
            return ''
%>
<DIV class=main>
  <DIV class=pages>
    <UL>
      <LI ${cur_class('*Main')|n}>
        <A href="${request.route_url('home')}">Main</A>
    % if user:
      <LI ${cur_class('*Users')|n}>
        <A href="${request.route_url('users')}">Users</A>
      <LI ${cur_class('*Files')|n}>
        <A href="${request.route_url('files')}">Files</A>
      <LI ${cur_class('*New Page')|n}>
        <A href="${request.route_url('new_page')}">Add New Page</A>
    % endif
    % for post in menu_pages:
      <LI ${cur_class(post.page)|n}>
        <A href="${request.route_url('posts',page=post.page, skip=0)}"
                >${post.page}</A>
    % endfor
    </UL>

  </DIV>
  <DIV class="content">
