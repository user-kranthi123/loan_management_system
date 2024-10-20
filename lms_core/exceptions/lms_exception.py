class LoanException(Exception):
    def __init__(self, message="Details are not valid!"):
        self.message = message
        super().__init__(self.message)
class PaymentException(Exception):
    def __init__(self, message="Invalid payment!"):
        self.message = message
        super().__init__(self.message)
class CustomerNotEligible(Exception):
    def __init__(self, message="Customer is not eligible for this loan"):
        self.message = message
        super().__init__(self.message)
class UserException(Exception):
    def __init__(self, message="Invalid User!"):
        self.message = message
        super().__init__(self.message)
class DocumentException(Exception):
    def __init__(self, message="Unable to upload document to s3"):
        self.message = message
        super().__init__(self.message)