const addModalHelper = {
	showBranches: (branchesData, content, completeMessage, ws) => {
		// Clear loader and button:

		$("#loaderEllipsis").hide()
		$("#fetchRepoButton").hide()
		$("#loadingTextAppSubmit").text("")

		if (!("branches" in branchesData)) {
			sendNotification(
				"Error while checking the repo for branches. Please ensure the repo is public.",
				$("#branchesList")
			)
			return
		}

		if (branchesData["branches"].length == 1) {
			sendNotification(
				`One branch found. Continuing packaging with ${
					branchesData["branches"][0]
				} branch.`,
				$("#branchesList")
			)
			$("#loaderEllipsis").show()
			$("#processBranchButton").prop("disabled", true)
			$("#loadingTextAppSubmit").text(
				`Please wait. Processing branch: ${branchesData["branches"][0]}`
			)

			notification_ws.send(
				JSON.stringify({
					data: {
						branch: branchesData["branches"][0],
						github_dir: branchesData["github_dir"]
					},
					type: `process_branch`
				})
			)
			return
		}

		// More than one branch available. Ask user for option:
		let branchesHTML = htmlHelpers.getBranches(branchesData["branches"])
		$("#branchesList").append(branchesHTML)

		$("#processBranchButton").click((e) => {
			let branchName = $("#add_branch").val()

			$("#loaderEllipsis").show()
			$("#processBranchButton").prop("disabled", true)
			$("#loadingTextAppSubmit").text(
				`Please wait. Processing branch: ${branchName}`
			)

			notification_ws.send(
				JSON.stringify({
					data: {
						branch: branchName,
						github_dir: branchesData["github_dir"]
					},
					type: `process_branch`
				})
			)
		})
		$("#processBranchButton").show()
	},
	addComplete: (addData, content, completeMessage, ws) => {
		$("#loaderEllipsis").hide()
		$("#processBranchButton").hide()
		$("#cancelAddButton").hide()
		$("#loadingTextAppSubmit").text("")
		$("#doneAddButton").show()
		$("#successMessage").show()
	}
}
