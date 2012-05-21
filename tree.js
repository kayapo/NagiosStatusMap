var radius = 420;
var nodes;

var tree = d3.layout.tree()
    .size([380, 380])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

var diagonal = d3.svg.diagonal.radial()
    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

var vis = d3.select("#chart").append("svg")
    .attr("width", radius * 2)
    .attr("height", radius * 2)
    .append("g")
    .attr("transform", "translate(" + radius + "," + radius + ")");

d3.json("data.json", function(json) {
  nodes = tree.nodes(json);

  var link = vis.selectAll("path.link")
      .data(tree.links(nodes))
      .enter().append("path")
      .attr("class", function(d) { return "link" + d.target.link; } )
      .attr("d", diagonal);

  var node = vis.selectAll("g.node")
      .data(nodes)
      .enter().append("g")
      .attr("class", function(d) { return ( "node" + d.status ) } )
      .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })

  node.append("circle")
      .attr("r", function(d) { return ( d.size / 2.25 ) })
      .on("mousemove", showstatus)
      .on("mouseout", hidestatus);

  node.append("text")
      .attr("x", function(d) { return d.x < 180 ? ".67em" : "-.67em"; })
      .attr("dy", ".43em")
      .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
      .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })
      .text(function(d) { return d.name; });
});

var svg = d3.select("#chart").select("svg");

showstatus = function(d, i) {
  var mp = d3.mouse(svg[0][0]);
  if ( svg.select("rect") )
      svg.select("rect").remove();
      
  if ( svg.select(( "#pt" + i )) )
      svg.select(( "#pt" + i )).remove();

  svg.append("rect")
      .attr("x", (mp[0] + 5))
      .attr("y", (mp[1] + 5))
      .attr("rx", 10)
      .attr("ry", 10)
      .attr("width", 240)
      .attr("height", 40)
      .attr("class", "popup");

  svg.append("text")
      .attr("id", ( "pt" + i ))
      .attr("x", (mp[0] + 15))
      .attr("y", (mp[1] + 20))
      .attr("text-anchor", "start")
      .text(d.name);
}

hidestatus = function(d, i) {
  svg.select("rect").remove();
  svg.select(( "#pt" + i )).remove();
}