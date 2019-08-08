$( function() {
    $.widget( "custom.catcomplete", $.ui.autocomplete, {
      _create: function() {
        this._super();
        this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
      },
      _renderMenu: function( ul, items ) {
        var that = this,
          currentCategory = "";
        $.each( items, function( index, item ) {
          var li;
          if ( item.category != currentCategory ) {
            ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
            currentCategory = item.category;
          }
          li = that._renderItemData( ul, item );
          if ( item.category ) {
            li.attr( "aria-label", item.category + " : " + item.label );
          }
        });
      }
    });
    var data = [
      { label: "Ultrasound Knee Right", category: "Ultrasound" },
      { label: "Ultrasound Knee Left", category: "Ultrasound" },
      { label: "MRI Knee Right", category: "MRI" },
      { label: "MRI Knee Left", category: "MRI" },
      { label: "CT Knee Right", category: "CT" },
      { label: "CT Knee Left", category: "CT" },
      { label: "Ultrasound Forearm/Elbow Left", category: "Ultrasound" },
      { label: "Ultrasound Forearm/Elbow Right", category: "Ultrasound" },
      { label: "MRI Forearm/Elbow Left", category: "MRI" },
      { label: "MRI Forearm/Elbow Right", category: "MRI" },
      { label: "CT Forearm/Elbow Left", category: "CT" },
      { label: "CT Forearm/Elbow Right", category: "CT" }
    ];
 
     var inputText1 = [
         { label: 'Within expected limits', category: " " },
         { label: 'Amplitude reduced', category: " " },
         { label: 'Amplitude reduced, delayed', category: " " },
         { label: 'Amplitude within expected limits, delayed', category: " " },
         { label: 'Not measurable above noise', category: " " },
         { label: 'Unreliable', category: " " }
     ];
    
     var inputText2 = [
         { label: 'a-wave and b-wave within expected limits', category: " " },
         { label: 'a-wave and b-wave within expected limits, delayed', category: " " },
         { label: 'a-wave within expected limits, b-wave amplitude reduced', category: " " },
         { label: 'a-wave and b-wave amplitude reduced', category: " " },
         { label: 'a-wave and b-wave amplitude reduced, delayed', category: " " },
         { label: 'Not measurable above noise', category: " " },
         { label: 'Unreliable' }
     ];

     var inputText3 = [
         { label: 'Within expected limits', category: " " },
         { label: 'Preserved, amplitude reduced', category: " " },
         { label: 'Not measurable above noise', category: " " }
     ];

 
    $( ".erg-input-1" ).catcomplete({
      delay: 0,
      source: inputText1
    });

    $( ".erg-input-2" ).catcomplete({
      delay: 0,
      source: inputText2
    });
    
    $( ".erg-input-3" ).catcomplete({
      delay: 0,
      source: inputText3
    });

  } );
  
// form button autofill function
$(".report-select").on("click", function(){
    $t = $(this).text()
    $(this).closest(".erg-control").find(".erg-input").val($t)
});


