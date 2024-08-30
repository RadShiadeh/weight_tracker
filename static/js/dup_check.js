function dup_check(duplicate) {
    if (duplicate === 'true') {
        const userConfirmation = confirm("An entery for the selected date exists, do you wish to update it?")

        if (userConfirmation) {
            document.getElementById('duplicate-update-form').submit();
            alert("entry updated!")
        } else {
            alert("keeping the old entry")
        }
    }
}