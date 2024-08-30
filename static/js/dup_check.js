function dup_check(duplicate) {
    if (duplicate === 'true') {
        const userConfirmation = confirm("An entery for the selected date exists, do you wish to update it?")

        if (userConfirmation) {
            alert("entry will be updated!")
            document.getElementById('duplicate-update-form').submit();
        } else {
            alert("keeping the old entry")
        }
    }
}