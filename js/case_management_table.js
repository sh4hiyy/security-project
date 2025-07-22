// This Script Below is filtering of case status
$(document).ready(function() {
    // Initialize datatables. Data table from external vendors
    var table = $('#dataTable').DataTable();

    // Event listener for the status filter dropdown
    $('#statusFilter').on('change', function() {
        var selectedStatus = $(this).val(); // This get the dropdown filter value
        table.draw(); //Activate DataTables draw event to apply the filter which changed/refresh the table
    });

    // Custom filter function for DataTables due to the icon at the side :C
    $.fn.dataTable.ext.search.push( // This code extracts the data table lib, Jquery identifer, inherit from the constructor's prototype.
        // More info about the above: https://datatables.net/forums/discussion/72500/pass-value-to-fn-datatable-ext-search-push and https://datatables.net/manual/tech-notes/10#How-to-provide-a-test-case

        function(settings, data, dataIndex) { //With the above code, get settings, data and data index from the row

            // Get the value of the selected status from the dropdown
            var selectedStatus = $('#statusFilter').val();
            // Get the status of the current row (using the data-status attribute)
            var status = $(table.row(dataIndex).node()).find('td[data-status]').data('status');
            
            // If the selected status is empty or it matches the row's status, include the row
            if (selectedStatus === '' || status === selectedStatus) {
                return true;
            }
            // Otherwise, exclude the row
            return false;
        }
    );

    // Trigger the change event to apply the initial filter (if any)
    $('#statusFilter').trigger('change');
});


$(document).ready(function() {
    // Event delegation for delete button
    $(document).on('click', '.case_delete', function(event) {
        event.preventDefault();
        const caseId = $(this).data('case-id');

        if (confirm(`Are you sure you want to delete case ID: ${caseId}?`)) {
            $.post(`/delete_case/${caseId}`, function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert(`Error deleting case: ${response.error}`);
                }
            });
        }
    });

    // Event delegation for close button
    $(document).on('click', '.case_closed', function(event) {
        event.preventDefault();
        const caseId = $(this).data('case-id');

        if (confirm(`Are you sure you want to close case ID: ${caseId}?`)) {
            $.post(`/close_case/${caseId}`, function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert(`Error closing case: ${response.error}`);
                }
            });
        }
    });

    $(document).on('click', '.faq_delete', function(event) {
        event.preventDefault();
        const faqId = $(this).data('faq-id');

        if (confirm(`Are you sure you want to delete FAQ ID: ${faqId}?`)) {
            $.post(`/delete_faq/${faqId}`, function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert(`Error deleting FAQ: ${response.error}`);
                }
            });
        }
    });
});


