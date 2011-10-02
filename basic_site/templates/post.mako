<%include file="head.mako" />
<% 
    route_url = request.route_url
    edit_url = route_url('edit', ptype='post', id=post.id)
    if prior is not None:
        prior_url = route_url('post', id='%s.%d' % (post.id, prior)) 
    if next >= 0:
        next_url = route_url('post', id='%s.%d' % (post.id, next)) 
    if next is not None:
        current_url = route_url('post', id=post.id)
    if prior is not None and prior > 0:
        restore_url = route_url('restore', ptype='post',
                                id=post.id, skip=prior-1)
    else:
        restore_url = None
%>

<DIV class="post">
  <H2>${post.title}</H2>    
  ${post.render()|n}
  <DIV class="footer">
    <SPAN class="creator">${post.creator|h}</SPAN>
    <SPAN class="created">${post.created|h}</SPAN>
    % if user and prior == 0:
      <A href="${edit_url}">edit</A>
    % elif user and restore_url:
      <A href="${restore_url}">restore</A>
    % endif 
    % if user and (prior is not None or next is not None):
      versions:
      % if prior is not None:
        <A href="${prior_url}">older</A>
      % endif
      % if next >= 0:
        <A href="${next_url}">newer</A>
      % endif
      % if next is not None:
        <A href="${current_url}">current</A>
      % endif
    % endif
  </DIV>
</DIV>
<%include file="foot.mako" />
