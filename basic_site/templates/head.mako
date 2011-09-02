<HTML>
<HEAD>
    <TITLE>${request.registry.settings['site_name'] + page_subtitle|h}</TITLE>
    <LINK type="text/css" rel="stylesheet"
          href="${request.static_url('basic_site:static/base.css')}">
</HEAD>
<DIV id="head">
    <IMG src="${request.route_url('file',name='logo.png',rev='')}">
    <DIV id="login">
  % if user == None:
      <FORM action='' method="POST">
        <LABEL target="user">User</LABEL>
        <INPUT type="text" name="user"> 
        <LABEL target="passwd">Password</LABEL>
        <INPUT type="password" name="passwd">
        <BUTTON type="submit">Login</BUTTON>
      </FORM>
  % else:
      Logged in as <STRONG>${user.uid}</STRONG> 
      (<A href="${request.route_url('logout')}">logout</A>)
  % endif
    </DIV>
</DIV>

<%
    def cur_class(this_page):
        if this_page == page_name:
            return 'class="current"'
        else:
            return ''
%>
<DIV id=pages>
  <UL>
    <LI><A href="${request.route_url('home')}" ${cur_class('*Main')}>Main</A>
  % if user:
    <LI><A href="${request.route_url('users')}" 
           ${cur_class('*Users')}>Users</A>
    <LI><A href="${request.route_url('files')}"
           ${cur_class('*Files')}>Files</A>
  % endif
  % for page in menu_pages:
    <LI><A href="${request.route_url('page', id=page.id)}">grarg</A>
  % endfor
  </UL>
</DIV>

% if message:
    <DIV class="message">${message|h}</DIV>
% endif
