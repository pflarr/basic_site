<%include file="head.mako" />


% if user:
<DIV><A href="${request.route_url('add', page=page_name)}"
     >Add a new Post</A></DIV>
% endif
% for post in posts:
  <% 
    edit_url = request.route_url('edit', page=post.page, id=post.id)
  %> 
  <DIV class="post">
    <H2>${post.title}</H2>
    ${post.render()|n}
    <DIV class="post_footer">
      <SPAN class="creator">${post.creator|h}</SPAN>
      <SPAN class="created">${post.created|h}</SPAN>
    % if user:
      <A href="${edit_url}">edit</A>
      <A href="${request.route_url('post',id=post.id)}">versions</A>
    % endif
    </DIV>
  </DIV>
% endfor

<%include file="foot.mako" />
