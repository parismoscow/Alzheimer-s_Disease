function init() {
  // Grab a reference to the dropdown select element
  // var selector = d3.select("#selDataset");
  //
  // // Use the list of sample names to populate the select options
  // d3.json("/names").then((sampleNames) => {
  //   sampleNames.forEach((sample) => {
  //     selector
  //       .append("option")
  //       .text(sample)
  //       .property("value", sample);
  //   });
  //
  //   // Use the first sample from the list to build the initial plots
  //   const firstSample = sampleNames[0];
  //   buildCharts(firstSample);
  //   buildMetadata(firstSample);
  // });
  selectionChanged()
}

async function buildCharts(sample) {

  const thisSample = await d3.json(`/samples/${sample}`)

  // create an array of objects for easier sorting
  let sampleList = []

  for (i=0; i<thisSample.sample_values.length; i++) {
    sampleObject = {
      "otu_ids": thisSample.otu_ids[i],
      "otu_labels": thisSample.otu_labels[i],
      "sample_values": thisSample.sample_values[i]
    }
    sampleList.push(sampleObject)
  }

  // sort the array on sample_values, in descending order
  sampleList = sampleList.sort(function(a,b) {
    return b.sample_values - a.sample_values
  })

  buildPie(sampleList.slice(0,10))
  buildBubble(sampleList, sample)
}

function buildPie (data) {
  otu_ids =  unpack(data, "otu_ids")
  otu_labels = unpack(data, "otu_labels")
  sample_values = unpack(data, "sample_values")

  const trace = {
    values: sample_values,
    labels: otu_ids,
    names: otu_labels,
    type: "pie",
    mode: 'markers',
    hovertext: otu_labels,
    hoverinfo: 'label+percent+text',
  }
  // display the pie chart
  data = [trace]
  Plotly.newPlot("pie", data);
}


async function selectionChanged () {
  // Fetch new data each time a new selection is made
  // var Selections = ['model', 'prediction', 'oversampling', 'scaling']
  // var dataSet = ['demographic', 'apoe4', 'cogtest', 'mri', 'mripct', 'pet', 'csf']
  // var temparr = []
  const dict  = {}

  dict['model'] = d3.select('#model').property('value')
  dict['prediction'] = d3.select('#prediction').property('value')
  dict['oversampling'] = d3.select('#oversampling').property('value')
  dict['scaling'] = d3.select('#scaling').property('value')
  if (d3.select('#demographic').property('checked')){
    dict['demographic'] = d3.select('#demographic').property('value')
  }
  if (d3.select('#apoe4').property('checked')){
    dict['apoe4'] = d3.select('#apoe4').property('value')
  }
  if (d3.select('#cogtest').property('checked')){
    dict['cogtest'] = d3.select('#cogtest').property('value')
  }
  if (d3.select('#mri').property('checked')){
    dict['mri'] = d3.select('#mri').property('value')
  }
  if (d3.select('#mripct').property('checked')){
    dict['mripct'] = d3.select('#mripct').property('value')
  }
  if (d3.select('#pet').property('checked')){
    dict['pet'] = d3.select('#pet').property('value')
  }
  if (d3.select('#csf').property('checked')){
    dict['csf'] = d3.select('#csf').property('value')
  }

// console.log(dict);
  // Selections.forEach(function(selection) {
  //   const id = `#${selection}`
  //   // d3.select("#selDataset")
  //   value = d3.select(`${id}`).property('value')
  //   // console.log(value);
  //   dict[selection] = value
  //   console.log(`setting dict[${selection}] to ${dict[selection]}`)
  //   console.log(`returning ${dict[sampling]}`)
  //
  //   // temparr.push(value)
  // });
  //
  // dataSet.forEach(function(selection){
  //   checkbox = d3.select(`#${selection}`)
  //   if (checkbox.property('checked')) {
  //     dict[selection] = checkbox.property('value')
  //     console.log(`setting dict[${selection}] to ${dict[selection]}`)
  //
  //     // temparr.push(checkbox.property('value'))
  //   }
  // })
  // console.log(`returning ${dict[sampling]}`)
  temp = JSON.stringify(dict);
  // console.log(JSON.stringify({ x: 5, y: 6 }));

  // const dict2 = {'key': 'value'}
// temp = JSON.stringify(dict2);
  // console.log(`returning ${temp}`)

  const modelStats = await d3.json(`/getdata/${temp}`)
  // console.log(`received ${data} back from python`);
  data = modelStats['data']
  layout = modelStats['layout']
  console.log(`layout is: ${layout}`);
  // layout =

  Plotly.newPlot("roc_curve", data, layout)
}

// Initialize the dashboard
// init();
// selectionChanged()
