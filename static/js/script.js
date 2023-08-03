function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable");
    switching = true;
    // Set the sorting direction to descending:
    dir = "desc"; 
    // Remove the sort symbol from all columns:
    for (i = 0; i < 5; i++) {
      table.rows[0].getElementsByTagName("TH")[i].innerHTML = table.rows[0].getElementsByTagName("TH")[i].innerHTML.replace(" ▲", "").replace(" ▼", "");
    }
    while (switching) {
      switching = false;
      rows = table.rows;
      for (i = 1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        if (dir == "desc") {
          if (n === 3) { // if it's the progress bar column
            var xVal = x.getElementsByTagName("progress")[0].value;
            var xMax = x.getElementsByTagName("progress")[0].max;
            var yVal = y.getElementsByTagName("progress")[0].value;
            var yMax = y.getElementsByTagName("progress")[0].max;
            if ((xVal / xMax) < (yVal / yMax)) {
              shouldSwitch = true;
              break;
            }
          } else if (isNaN(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) { // if it's a string
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
              shouldSwitch = true;
              break;
            }
          } else { // if it's a number
            if (Number(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', '')) < Number(y.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) {
              shouldSwitch = true;
              break;
            }
          }
        } else if (dir == "asc") {
          if (n === 3) { // if it's the progress bar column
            var xVal = x.getElementsByTagName("progress")[0].value;
            var xMax = x.getElementsByTagName("progress")[0].max;
            var yVal = y.getElementsByTagName("progress")[0].value;
            var yMax = y.getElementsByTagName("progress")[0].max;
            if ((xVal / xMax) > (yVal / yMax)) {
              shouldSwitch = true;
              break;
            }
          } else if (isNaN(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) { // if it's a string
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
              shouldSwitch = true;
              break;
            }
          } else { // if it's a number
            if (Number(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', '')) > Number(y.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) {
              shouldSwitch = true;
              break;
            }
          }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;      
      } else {
        if (switchcount == 0 && dir == "desc") {
          dir = "asc";
          switching = true;
        }
      }
    }
    // Add the sort symbol to the sorted column:
    if (dir == "asc") {
      table.rows[0].getElementsByTagName("TH")[n].innerHTML += " ▼";
    } else if (dir == "desc") {
      table.rows[0].getElementsByTagName("TH")[n].innerHTML += " ▲";
    }
  }
  