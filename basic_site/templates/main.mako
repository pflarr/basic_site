<%include file="head.mako" />


<DIV id="content">
% if user:
<DIV><A href="${request.route_url('add', ptype='post', mode='add')}"
     >Add a new Post</A></DIV>
% endif
% for post in posts:
  <DIV class="news">
    ${post.content}
    <DIV class="news_footer">
      <SPAN class="creator">${post.creator|h}</SPAN>
      <SPAN class="created">${post.created|h}</SPAN>
      <A href="${request.route_url('edit', post.id)}"></A>
    </DIV>
  </DIV>
% endfor
</DIV>

<%include file="foot.mako" />
