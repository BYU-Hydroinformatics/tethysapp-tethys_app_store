//Upload snow WaterML file to HydroShare
var displayStatus = $("#display-status")

$("#hydroshare-proceed").on("click", function() {
    //This function only works on HTML5 browsers.
    console.log("running hydroshare-proceed!!")

    //now we construct the WaterML..
    var waterml_link = $("#waterml-link").attr("href")
    var upload_link = waterml_link.replace("waterml", "upload-to-hydroshare")
    // console.log(waterml_link)

    displayStatus.removeClass("error")
    displayStatus.addClass("uploading")
    displayStatus.html("<em>Uploading...</em>")
    var resourceTypeSwitch = function(typeSelection) {
        var options = {
            Generic: "GenericResource",
            "Geographic Raster": "RasterResource",
            "HIS Referenced Time Series": "RefTimeSeries",
            "Model Instance": "ModelInstanceResource",
            "Model Program": "ModelProgramResource",
            "Multidimensional (NetCDF)": "NetcdfResource",
            "Time Series": "TimeSeriesResource",
            Application: "ToolResource"
        }
        return options[typeSelection]
    }

    var resourceAbstract = $("#resource-abstract").val()
    var resourceTitle = $("#resource-title").val()
    var resourceKeywords = $("#resource-keywords").val()
        ? $("#resource-keywords").val()
        : ""
    var resourceType = resourceTypeSwitch($("#resource-type").val())

    if (!resourceTitle || !resourceKeywords || !resourceAbstract) {
        displayStatus.removeClass("uploading")
        displayStatus.addClass("error")
        displayStatus.html("<em>You must provide all metadata information.</em>")
        return
    }

    upload_link =
        upload_link +
        "&title=" +
        resourceTitle +
        "&abstract=" +
        resourceAbstract +
        "&keywords=" +
        resourceKeywords

    $(this).prop("disabled", true)
    $.ajax({
        type: "GET",
        url: upload_link,
        dataType: "json",
        success: function(data) {
            debugger
            $("#hydroshare-proceed").prop("disabled", false)
            if ("error" in data) {
                displayStatus.removeClass("uploading")
                displayStatus.addClass("error")
                displayStatus.html("<em>" + data.error + "</em>")
            } else {
                displayStatus.removeClass("uploading")
                displayStatus.addClass("success")
                displayStatus.html(
                    "<em>" +
                        data.success +
                        ' View in HydroShare <a href="https://www.hydroshare.org/resource/' +
                        data.newResource +
                        '" target="_blank">HERE</a></em>'
                )
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert("Error")
            debugger
            $("#hydroshare-proceed").prop("disabled", false)
            console.log(jqXHR + "\n" + textStatus + "\n" + errorThrown)
            displayStatus.removeClass("uploading")
            displayStatus.addClass("error")
            displayStatus.html("<em>" + errorThrown + "</em>")
        }
    })
})
