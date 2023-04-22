# class Workplace:
#     static_workplace_id = 1
#
#     def __init__(self, company_name, description, industry, website, specialities, is_generating_id=True):
#         if is_generating_id:
#             # automatic id assignment to seller
#             self.id = Workplace.static_workplace_id
#             Workplace.static_workplace_id += 1
#         else:
#             # id will be declared manually
#             self.id = None
#
#         self.company_name = company_name
#         self.description = description
#         self.industry = industry
#         self.website = website
#         self.specialities = specialities
#
#     def __dict__(self):
#         return {
#             'id': self.id,
#             'company_name': self.company_name,
#             'description': self.description,
#             'industry': self.industry,
#             'website': self.website,
#             'specialities': self.specialities
#         }

