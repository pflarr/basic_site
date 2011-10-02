<%include file="head.mako" />
<% 
    route_url = request.route_url
    edit_url = route_url('edit', ptype='page', id=page.id)
    if prior is not None:
        prior_url = route_url('page', name='%s.%d' % (page_name, prior)) 
    if next >= 0:
        next_url = route_url('page', name='%s.%d' % (page_name, next)) 
    if next is not None:
        current_url = route_url('page', name=page_name)
%>
<DIV class="page">
    <H1>${page.name}</H1>
    ${page.render()|n}
    <DIV class="page_footer">
      <SPAN class="creator">${page.creator|h}</SPAN>
      <SPAN class="created">${page.created|h}</SPAN>
    % if user and prior is None and next is None:
      <A href="${edit_url}">edit</A>
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
