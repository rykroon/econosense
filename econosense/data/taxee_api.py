import requests

class TaxeeApi:
    API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVhZGI1N2EyNTZhOTBlMDc3Yjk1MTc0NCIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTUyNDMyNDI1OH0.L5po7FlCskM3n5QynHv3_P1gszmYNKlMwoYfekIWht0'
    header = {'Authorization':'Bearer ' + API_KEY}
    federal_tax_url = "https://taxee.io/api/v2/federal/"
    state_tax_url = "https://taxee.io/api/v2/state/"
    income_tax_url = "https://taxee.io/api/v2/calculate/"


    def get_federal_tax_brackets(self,year):
        url = self.federal_tax_url + str(year)
        response = requests.get(url,headers=self.header)
        return self._handle_response(response)


    def get_state_tax_brackets(self,year,state):
        url = self.state_tax_url + str(year) + '/' + state
        response = requests.get(url,headers=self.header)
        return self._handle_response(response)


    def get_income_tax_response(self,year,gross,filing_status,state):
        url = self.income_tax_url + str(year)
        data = {'pay_rate':gross,'filing_status':filing_status,'state':state}
        response = requests.post(url,data=data,headers=self.header)
        return self._handle_response(response)


    def get_income_taxes(self,year,gross,filing_status,state):
        response = self.get_income_tax_response(year,gross,filing_status,state)
        if response is not None:
            fica = response['annual']['fica']['amount']
            federal = response['annual']['federal']['amount']
            state = response['annual']['state']['amount']
            if state == None: state = 0
            return {'fica':fica,'federal':federal,'state':state}
        else:
            return None


    def get_net_income(self,year,gross,filing_status,state):
        taxes = self.get_income_taxes(year,gross,filing_status,state)
        if taxes is not None:
            return gross - taxes['fica'] - taxes['federal'] - taxes['state']
        else:
            return None


    def _handle_response(self,response):
        if response.status_code == 200: return response.json()
        else: return None


# year = 2016
# gross = 50000
# filing_status = 'single'
# state = 'FL'
#
# tax = TaxeeApi()
#
# income_tax = tax.get_income_tax_response(year,gross,filing_status,state)
# print(income_tax)
#
# taxes = tax.get_income_taxes(year,gross,filing_status,state)
# print(taxes)
#
# net = tax.get_net_income(year,gross,filing_status,state)
# print(net)
# print('\n')
#
# state = 'NY'
#
# # income_tax = tax.get_income_tax_response(year,gross,filing_status,state)
# # print(income_tax)
#
# taxes = tax.get_income_taxes(year,gross,filing_status,state)
# print(taxes)
#
# net = tax.get_net_income(year,gross,filing_status,state)
# print(net)
# print('\n')
#
# year = '2017'
#
# # income_tax = tax.get_income_tax_response(year,gross,filing_status,state)
# # print(income_tax)
#
# taxes = tax.get_income_taxes(year,gross,filing_status,state)
# print(taxes)
#
# net = tax.get_net_income(year,gross,filing_status,state)
# print(net)
#
#
#
# # response = tax.get_federal_tax_brackets(year)
# # print(response)
# # print('\n')
# #
# # response = tax.get_state_tax_brackets(year,state)
# # print(response)
# # print('\n')
