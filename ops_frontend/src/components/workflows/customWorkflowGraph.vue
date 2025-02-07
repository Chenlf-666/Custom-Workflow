<template>
  <div style="display: flex; align-items: center">
    <div style="border: 1px solid #ccc; padding: 20px; width: 1500px">
      <svg class="dagre" width="1500" height="800">
        <g class="container"></g>
      </svg>
    </div>
  </div>
</template>
  
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { getTransitions, getWorkflowStatus } from "../../api/cusWorkflow";
import dagreD3 from "dagre-d3";
import * as d3 from "d3";

const props = defineProps({
  workflowId: {
    type: Number,
    required: false
  },
  tabIndex: {
    type: String,
    required: false
  }
})

const edges = <any>ref({});
const nodes = <any>ref({});


const handleCanvasClick = (graph) => {
  // 取消选中所有边
  graph.edges().forEach(edge => {
    graph.setEdge(edge, { selected: false });
  });

  // 取消选中所有节点
  graph.nodes().forEach(node => {
    graph.setNode(node, { selected: false });
  });
};


const draw = () => {
  // 创建 Graph 对象
  // d3.select("svg.dagre g.container").selectAll("*").remove(); // 清除之前的内容

  const g = new dagreD3.graphlib.Graph()
  .setGraph({
    zoom: 1,
    rankdir: "TB", // 流程图从下向上显示，默认'TB'，可取值'TB'、'BT'、'LR'、'RL'
    //ranker: "network-simplex",//连线算法
    // nodesep: 70, // 节点之间间距
    // ranksep: 100, // 层与层之间的间距
  })
  .setDefaultEdgeLabel(function () {
      return {};
    });
  nodes.value.forEach((node) => {
    g.setNode(node.id, {
      id: node.id,
      label: `<foreignObject id='${node.id}'  width='300' height='80' >
        <div id='${
          node.id
        }'  xmlns='http://www.w3.org/1999/xhtml' style='width:300px; height: 80px' >
          <div id='${node.id}' class='nodeBox' style='text-align: center'>
            <span id='${node.id}' class='nodeA'>${node.name}</span>
          </div>
        </div>
        </foreignObject>`, //node.nodeName,
      labelType: "html",
      width: 320,
      height: 86,
      // shape: "rect", //节点形状，可以设置rect(长方形),circle,ellipse(椭圆),diamond(菱形) 四种形状，还可以使用render.shapes()自定义形状
      style: "fill:#fff;stroke:#a0cfff;stroke-width: 2px;cursor: pointer", //节点样式,可设置节点的颜色填充、节点边框
      labelStyle: "fill: #fff;font-weight:bold;cursor: pointer", //节点标签样式, 可设置节点标签的文本样式（颜色、粗细、大小）
      rx: 5, // 设置圆角
      ry: 5, // 设置圆角
      // paddingBottom: 0,
      // paddingLeft: 0,
      // paddingRight: 0,
      // paddingTop: 0,`
    });
  });

    // Graph添加节点之间的连线
  if (nodes.value.length > 1) {
    edges.value.forEach((edge) => {
      g.setEdge(edge.start, edge.end, {
        //curve: d3.curveStepBefore , //d3.curveBasis, // 设置为贝塞尔曲线
        style: "stroke: #0fb2cc; fill: none; stroke-width: 2px", // 连线样式
        arrowheadStyle: "fill: #0fb2cc;stroke: #0fb2cc;", //箭头样式，可以设置箭头颜色
        arrowhead: "vee", //箭头形状，可以设置 normal,vee,undirected 三种样式，默认为 normal
        label: edge.label, // 添加 label 信息
        labelStyle: "fill: #0fb2cc; font-weight: bold;" // 设置 label 样式
      });
    });
  }

  // 获取要绘制流程图的绘图容器
  const container = d3.select("svg.dagre").select("g.container");

// 创建渲染器
  const render = new dagreD3.render();
  // 在绘图容器上运行渲染器绘制流程图
  render(container, g);
  const svg = d3.select("svg.dagre");

  const graph = g;
  
  svg.on("click", function(event) {
  event.stopPropagation(); // 使用 stopPropagation
  handleCanvasClick(graph);
}, { passive: false }); // 确保这里也是非被动的


  var zoom = d3
    .zoom() // 缩放支持
    .scaleExtent([0.5, 2]) // 缩放范围
    .on("zoom", function (current) {
      container.attr("transform", current.transform);
    }, { passive: false});
  svg.call(zoom); // 缩放生效
  let { clientWidth, clientHeight } = svg._groups[0][0];
  let { width, height } = g.graph();
 
  let initScale = Math.min(clientWidth / width, clientHeight / height);

  svg
    .transition()
    .duration(1000) // 1s完成过渡
    .call(
      zoom.transform,
      d3.zoomIdentity // 居中显示
        .translate(
          (clientWidth - width * initScale) / 2,
          (clientHeight - height * initScale) / 2
        )
        .scale(initScale) // 默认缩放比例
    );
}

watch(() => props.tabIndex, (newVal) => {
  if (newVal == "5") {
    nodes.value = [];
    edges.value = [];

    getWorkflowStatus(props.workflowId).then((res)=>{
      if (res && res.status == 200){
        nodes.value = res.data.results.map(stateItem => ({
          id: stateItem.id,
          name: stateItem.name,
          nodeName: stateItem.name,
        }));
      }
    }).finally(()=>{
      getTransitions(props.workflowId).then((res)=>{
        if (res && res.status == 200){
          edges.value = res.data.results.map(transitionItem => ({
            start: String(transitionItem.source_state),
            end: String(transitionItem.dest_state),
            label: transitionItem.name
          }));
        }
      }).finally(()=>{
        if (nodes.value.length && edges.value.length){
          draw();
        }
      })
    })
  }
})

</script>