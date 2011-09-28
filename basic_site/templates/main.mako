<%include file="head.mako" />


<DIV class="content">
% if user:
<DIV><A href="${request.route_url('add', ptype='post', mode='add')}"
     >Add a new Post</A></DIV>
% endif
% for post in posts:
  <DIV class="post">
    <H2>${post.title}</H2>
    ${post.render()|n}
    <DIV class="post_footer">
      <SPAN class="creator">${post.creator|h}</SPAN>
      <SPAN class="created">${post.created|h}</SPAN>
      <A href="${request.route_url('edit', mode='edit', ptype='post', id=post.id)}">edit</A>
    </DIV>
  </DIV>
% endfor
</DIV>

<%include file="foot.mako" />
