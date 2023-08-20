// Make sure to execute this code after your Dash app has loaded
// and initialized (e.g., after the 'DOMContentLoaded' event).
document.addEventListener('DOMContentLoaded', function() {
    // Access the DashApp namespace
    var dashApp = window.DashApp;
  
    // Now you can use dashApp to interact with the Dash app
    // components and manage its state.
    
    // For example, to get the value of an input component with id 'input-element-id':
    var inputValue = dashApp.get_input_value('input-element-id');
    
    // Or to update the value of a component with id 'output-element-id':
    dashApp.update_output('output-element-id', {props: {children: 'New Value'}});
    
    // ...and so on.
  });