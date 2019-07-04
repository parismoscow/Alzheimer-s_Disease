function displayReport(modelStats) {
  data = modelStats['data']
  layout = modelStats['layout']
  d3.select("#status").text("")
  Plotly.newPlot("roc_curve", data, layout)
  d3.select("#class_report").html(modelStats['class_report'])
  console.log(modelStats['class_report']);
}

async function selectionChanged () {
  // Fetch new data each time a new selection is made
  const dict  = {}
  // clear LogisticRegression
  d3.select('#status').text("Collecting data...")
  d3.select('#roc_curve').text("")
  d3.select('#class_report').text("")

  // create dictionary of user selection
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

  // try to obtain data from an existing model
  temp = JSON.stringify(dict);
  const modelStats = await d3.json(`/getdata/${temp}`)
  // if successful display model stats
  if (modelStats['success']) {
    displayReport(modelStats)
  }

  else {
    // train a new model
    d3.select('#status').text("Training the model....")
    const modelStats = await d3.json(`/newmodel/${temp}`)
    d3.select('#status').text("")
    if (modelStats['success'] == -1) {
        d3.select('#status').text("The data set is not available")
      console.log("this dataset is not available")
    }
    else if (modelStats['success'] == 0) {
      d3.select('#status').text("There was an issue with obtaining the model ("+modelStats['error'] +")")
      console.log("There was an issue with obtaining a model");
    }
    else {
      // if successful display model stats
      displayReport(modelStats)
    }
  }
}
