const addModalHelper = {
  validationResults: (validationData,content, completeMessage, ws ) =>{
    if(!validationData.metadata['next_move']){
      // $("#failMessage").html(validationData.mssge_string)
      // $("#failMessage").show()


      $(`#${addData.conda_channel}_failMessage`).html(validationData.mssge_string)
      $(`#${addData.conda_channel}_failMessage`).show()
      $("#loaderEllipsis").hide()
      $("#loadingTextAppSubmit").text("")
      $("#fetchRepoButton").prop("disabled", false)
    }
    else{
      // $("#failMessage").html(validationData.mssge_string)
      // $("#failMessage").show()
      $(`#${addData.conda_channel}_failMessage`).html(validationData.mssge_string)
      $(`#${addData.conda_channel}_failMessage`).show()
      notification_ws.send(
          JSON.stringify({
              data: {
                  url: validationData.metadata['submission_github_url']
              },
              type: `pull_git_repo`
          })
      )
    }

  },
  showBranches: (branchesData, content, completeMessage, ws) => {
    // Clear loader and button:

    $("#loaderEllipsis").hide()
    $("#fetchRepoButton").hide()
    $("#loadingTextAppSubmit").text("")

    if (!("branches" in branchesData)) {
      sendNotification(
        "Error while checking the repo for branches. Please ensure the repo is public.",
        // $("#branchesList")
        $(".branchesList")

      )
      return
    }

    if (branchesData["branches"].length == 1) {
      $(`#${branchesData["conda_channel"]}_spinner`).show(); 

      sendNotification(
        `One branch found. Continuing packaging with ${
          branchesData["branches"][0]
        } branch.`,
        // $("#branchesList")
        $(".branchesList")

      )
      $("#loaderEllipsis").show()
      $("#processBranchButton").prop("disabled", true)
      $("#loadingTextAppSubmit").text(
        `Please wait. Processing branch: ${branchesData["branches"][0]}`
      )

      // notification_ws.send(
      //   JSON.stringify({
      //       data: {
      //           url: githubURL
      //       },
      //       type: `validate_git_repo`
      //   })
      // )

      notification_ws.send(
        JSON.stringify({
          data: {
            branch: branchesData["branches"][0],
            conda_channel: branchesData["conda_channel"],
            github_dir: branchesData["github_dir"],
            github_token: branchesData["github_token"],
            conda_labels: branchesData["conda_labels"],
            github_organization: branchesData["github_organization"],
            email: $("#notifEmail").val(),
            dev_url: $("#githubURL").val()

          },
          type: `process_branch`
        })
      )
      return
    }

    // More than one branch available. Ask user for option:
    let branchesHTML = htmlHelpers.getBranches(branchesData["conda_channel"], branchesData["branches"])
    // $("#branchesList").append(branchesHTML)
    $(`#${branchesData["conda_channel"]}_branchesList`).append(branchesHTML)

    $("#processBranchButton").click((e) => {
      $(`#${branchesData["conda_channel"]}_spinner`).show(); 

      let branchName = $(`#${branchesData["conda_channel"]}_add_branch`).val()
      // let branchName = $("#add_branch").val()

      $("#loaderEllipsis").show()
      $("#processBranchButton").prop("disabled", true)
      $("#loadingTextAppSubmit").text(
        `Please wait. Processing branch: ${branchName}`
      )

      notification_ws.send(
        JSON.stringify({
          data: {
            branch: branchName,

            conda_channel: branchesData["conda_channel"],
            github_dir: branchesData["github_dir"],
            github_token: branchesData["github_token"],
            conda_labels: branchesData["conda_labels"],
            github_organization: branchesData["github_organization"],
            email: $("#notifEmail").val(),
            dev_url: $("#githubURL").val()
          },
          type: `process_branch`
        })
      )
    })
    $("#processBranchButton").show()
    // $("#failMessage").hide()
    $(`#${branchesData["conda_channel"]}_failMessage`).hide()


  },
  addComplete: (addData, content, completeMessage, ws) => {
    $("#loaderEllipsis").hide()
    $("#processBranchButton").hide()
    $("#cancelAddButton").hide()
    $("#loadingTextAppSubmit").text("")
    if (addData.job_url) {
      
      $(`#${addData.conda_channel}_addSuccessLink`).html(
        `<a href="${addData.job_url}" target="_blank">here</a>`
      )
      // $("#addSuccessLink").html(
      //   `<a href="${addData.job_url}" target="_blank">here</a>`
      // )
      
    } else {
      // Hide the link part of the success message
      $(`#${addData.conda_channel}_SuccessLinkMessage`).hide();
      // $("#SuccessLinkMessage").hide()

    }
    $("#doneAddButton").show()
    // $("#successMessage").show()
    $(`#${addData.conda_channel}_successMessage`).show();

    // $("#failMessage").hide()
    $(`#${addData.conda_channel}_failMessage`).hide()

    $(`#${addData["conda_channel"]}_spinner`).hide(); 
  }
}
