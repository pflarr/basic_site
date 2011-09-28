<%include file="head.mako" />

<%
if mode == 'edit':
    content = data.content
else:
    content = ''
%>

<DIV class="content">
  % if data:
    <DIV class="post">
    % if ptype=="post":
      <H2 class="preview">Preview: ${data.title}</H2>
    % elif ptype=="page":
      <H2 class="preview">Preview: ${data.name}</H2>
    % endif
      ${data.render()|n}
      <DIV class="post_footer">
        <SPAN class="creator">${data.creator|h}</SPAN>
        <SPAN class="created">${data.created|h}</SPAN>
      </DIV>
    </DIV>
  % endif
  <DIV id="instructions">
     
  </DIV>
    
  <h1>${ptype}</h1>

  <FORM action="${request.route_url(mode,mode=mode,ptype=ptype,id=id)}" 
        method="post">
  % if ptype == 'post':
    <LABEL for="title">Post Title:</LABEL>
    <INPUT name="title" type="text" size="30" maxlength="30"
           value="${data.title if data else ''|h}"><BR/>
  % elif ptype == 'page':
    <LABEL for="name">Page Name:</LABEL>
    <INPUT name="name" type="text" size="15" maxlength="15"
           value="${data.name if data else ''}"><BR/>
  % endif
  % if (mode,ptype) == ('edit','page'):
    <INPUT name="old_name" type="hidden" value="${data.name}">
  % endif
    <LABEL for="content">${ptype.capitalize()} content:</LABEL><BR/>
  <%
    content = data.content if data else '' 
  %>
    <TEXTAREA name="content" rows="20" cols="80">${content}</TEXTAREA>
    <INPUT name="mode" type="hidden" value="${mode}">
    <INPUT name="ptype" type="hidden" value="${ptype}"><BR/>
    <BUTTON type="submit" name="action" value="submit">Submit</BUTTON>
    <BUTTON type="submit" name="action" value="preview">Preview</BUTTON>
  </FORM>
</DIV>

<%include file="foot.mako" />
