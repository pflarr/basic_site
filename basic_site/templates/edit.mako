<%include file="head.mako" />

<%
if mode == 'edit_post':
    content = post.content
elif mode == 'edit_page':
    content = page.content
else:
    content = ''
%>

<DIV id="main">
  <DIV id="instructions">
     
  </DIV>

  <FORM action="${save_url}" method="post">
  % if mode == 'new_post':
    <INPUT name="title" type="text" size="30" maxlength="30">
  % elif mode == 'edit_post':
    <INPUT name="id" type="hidden" value="${post.name}">
    <INPUT name="title" type="text" size="30" 
           maxlength="30" value=${post.title}>
  % elif mode == 'new_page':
    <INPUT name="name" type="text" size="15" maxlength="15">
  % elif mode == 'edit_page':
    <INPUT name="old_name" type="hidden" value="${page.name}">
    <INPUT name="name" type="text" size="15" maxlength="15">
  % endif
    <TEXTAREA name="content" rows="50" cols="160">${content}</TEXTAREA>
    <INPUT name="mode" type="hidden" value="${mode}">
  </FORM>
</DIV>

<%include file="foot.mako" />
