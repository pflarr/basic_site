<%include file="head.mako" />

% if data:
  <DIV class="post">
  <H2 class="preview">Preview: ${data.title}</H2>
    ${data.render()|n}
    <DIV class="post_footer">
      <SPAN class="creator">${data.creator|h}</SPAN>
      <SPAN class="created">${data.created|h}</SPAN>
    </DIV>
  </DIV>
% endif
<DIV id="instructions">
Insert wiki syntax instructions here.   
</DIV>
 
<DIV>
    <FORM action="${request.route_url(mode, page=page, id=id)}" 
          method="post">
      <LABEL for="title">Post Title:</LABEL>
      <INPUT name="title" type="text" size="30" maxlength="30"
             value="${data.title if data else ''|h}"><BR/>
      <LABEL for="content">Post content:</LABEL><BR/>
    <%
      content = data.content if data else '' 
    %>
      <TEXTAREA name="content" rows="20" cols="80">${content}</TEXTAREA><BR>
      <BUTTON type="submit" name="action" value="submit">Submit</BUTTON>
      <BUTTON type="submit" name="action" value="preview">Preview</BUTTON>
    </FORM>
</DIV>

<%include file="foot.mako" />
