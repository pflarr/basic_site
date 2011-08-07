<%include file="head.mako" />

<DIV id="main">

% if current_user.admin:
  <DIV id="add_user">
    <H3>Add User:</H3>
    <FORM method="POST" 
          action="${request.route_url('mod_users', action='add')}">
      <LABEL for="uid">User Name:</LABEL>
      <INPUT type="text" maxlength="10" size="10" name="uid">
      <LABEL for="fullname">Full Name:</LABEL>
      <INPUT type="text" size="30" name="fullname">
      <LABEL for="passwd">Password:</LABEL>
      <INPUT type="password" size="20" name="passwd">
      <LABEL for="repeat">Password (again):</LABEL>
      <INPUT type="password" size="20" name="repeat">
      <LABEL for="admin">Admin:</LABEL>
      <INPUT type="checkbox" name="admin"> 
      <BUTTON type="submit">Add User</BUTTON>
    </FORM>
  </DIV>
%endif

<DIV id="change_pw">
  <H3>Change your password:</H3>
  <FORM method="POST" 
        action="${request.route_url('change_pw', c_uid=uid)}">
    <LABEL for="old">Current Password:</LABEL>
    <INPUT type="password" size="20" name="old">
    <LABEL for="passwd">New Password:</LABEL>
    <INPUT type="password" size="20" name="new">
    <LABEL for="repeat">New Password (again):</LABEL>
    <INPUT type="password" size="20" name="repeat">
    <BUTTON type="submit">Change Password</BUTTON>
  </FORM>
</DIV>

<DIV id="users">
  <TABLE>
    <TR><TH>User<TH>Full Name<TH>Admin
  % for user in users:
    <TR><TD>${user.uid}<TD>${user.fullname}
    % if current_user.admin:
      <%
        toggle_href = request.route_url('mod_user', action='toggle_admin',
                                                    uid=user.uid)
        delete_href = request.route_url('mod_user', action='delete',
                                                    uid=user.uid)
        is_admin = 'Yes' if user.admin else 'No'
      %>
        <TD><A href="${toggle_href}" 
               title="Toggle admin rights for this user.">${is_admin}</A>
        <TD><A href="${delete_href}" title="Delete this user">delete</A>
    % else:
        <TD>${'Yes' if user.admin else 'No'}
    % endif
  % endfor
  </TABLE>
</DIV>

</DIV>

<%include file="foot.mako" />
