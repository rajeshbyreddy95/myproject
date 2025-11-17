from django.urls import reverse

def user_nav_links(request):
    nav_links = {}
    if request.user.is_authenticated:
        if request.user.designation == 'clerk':
            nav_links = {
                # 'dashboard': reverse('clerk_dashboard'),
                # 'receipt_create': reverse('clerk_receipt_create'),
                # 'receipt_inbox': reverse('clerk_receipt_inbox'),
                # 'receipt_sent': reverse('clerk_receipt_sent'),
                # 'receipt_advance': reverse('clerk_receipt_advance'),
                # 'file_create': reverse('clerk_file_create'),
                # 'file_inbox': reverse('clerk_file_inbox'),
                # 'file_sent': reverse('clerk_receipt_sent'),  # or a dedicated URL
                # 'issue_sent': reverse('clerk_issue_sent'),
                # 'issue_returned': reverse('clerk_issue_returned'),
                # 'issue_advance': reverse('clerk_issue_advance'),
            }
        elif request.user.designation == 'superitendent':
            nav_links = {
                # 'dashboard': reverse('superi_dashboard'),
        #         'receipt_create': reverse('superintendent_receipt_create'),
                # 'receipt_inbox': reverse('superi_receipt_inbox'),
        #         'receipt_sent': reverse('superintendent_receipt_sent'),
        #         'receipt_advance': reverse('superintendent_receipt_advance'),
        #         'file_create': reverse('superintendent_file_create'),
        #         'file_inbox': reverse('superintendent_file_inbox'),
        #         'file_sent': reverse('superintendent_receipt_sent'),
        #         'issue_sent': reverse('superintendent_issue_sent'),
        #         'issue_returned': reverse('superintendent_issue_returned'),
        #         'issue_advance': reverse('superintendent_issue_advance'),
            }
    return {'nav_links': nav_links}
