
import ray
from ray import serve
from starlette.requests import Request
# import openai
from io import BytesIO
import pdfplumber
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_extraction_chain
from langchain.chat_models import ChatOpenAI
# import time

OPENAI_API_KEY = 'your openai api key s goes here'

@serve.deployment(max_concurrent_queries=20, route_prefix='/invoice', num_replicas=1)
class DeployLLM:
    def __init__(self):
        self.prompt_po = ChatPromptTemplate.from_messages(
        [("system","Given a text inputcontaining information about invoices and their relations between 'Buzz Network'\
        and other companies.Ensure that the model identifies the names of companies, excluding 'BUZZ WIRELESS NETWORKS LTD,'\
        and NEVER EVER return 'BUZZ WIRELESS NETWORKS LTD'as a company name.\
        If a particular detail is not present in the input, clearly indicate that it is missing.\
        Ensure that the model is flexible and can recognize different representations of the same variable.\
        always follow this guide:\
        1- never ever return 'Buzz Wireless Network' or 'BUZZ WIRELESS NETWORKS LTD,' or 'Buzz Wireless Network' as 'company name'\
        2-'purchase order', 'purchase No' and 'order No' are the same and used instead of each other"),
        ("human", "{input}"),
        ("ai", "?")])

        self.po_schema = {
        "properties": {
            "company name": {"type": "string"},
            "PURCHASE ORDER": {"type": "string"},
            "order No": {"type": "string"},
            "Quote Ref": {"type": "string"},
            "Net Amount": {"type": "integer"},
            "Total Due": {"type": "integer"},

        },

        "required": ["company name",  "PURCHASE ORDER","order No","Net Total",'Quote Ref'],
        }
        llm = ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,  model="gpt-4-1106-preview")
        self.po_chain = create_extraction_chain(self.po_schema, llm, self.prompt_po)
        self.prompt_invoice = ChatPromptTemplate.from_messages(
        [("system","Given a text inputcontaining information about invoices and their relations between 'Buzz Network'\
        and other companies.Ensure that the model identifies the names of companies, excluding 'BUZZ WIRELESS NETWORKS LTD,'\
        and NEVER EVER return 'BUZZ WIRELESS NETWORKS LTD'as a company name.\
        If a particular detail is not present in the input, clearly indicate that it is missing.\
        Account Numbers may appear in various formats such as 'A/C No.', 'Account No.'.\
        Ensure that the model is flexible and can recognize different representations of the same variable.\
        always follow this guide:\
        1- never ever return 'Buzz Wireless Network' or 'BUZZ WIRELESS NETWORKS LTD,' or 'Buzz Wireless Network' as 'company name'\
        2-'purchase order', 'purchase No' and 'order No' are the same and used instead of each other"),
        ("human" , "Invoice No: 1622487 Date: 09 June 2023 Accounts PayableBuzz Wireless Network Office 2 The Courtyard Bawtry Doncaster DN10 6JG KNW No.\
        Supplier No. Purchase order 01302 710 819 Kieran Feenix RE: Lantra-Landscape\
        Tools Multi-tool 26th - 27th June 2023 Accreditation 4 Candidates Equipment Hire - 4\
        Candidates Site Hire Net Amount VAT @ 20% Total Due Payment due immediately\
        Please note bank details National Westminster Bank PLC 2,\
        Howe Walk, Burnley, BB11 1NZ A/c No: 17887623 A/c Name: Kielder Newport West Ltd Sort Code: 01-01-35\
        Please make all cheques payable to Kielder Newport West Limited\
        If you have any queries regarding this invoice please contact KNW on (01677) 424633 VAT Reg No:\
        693 0290 30 £ AMOUNT 938.00 464.00 32.00 190.00 1,624.00 324.80 1,948.80"),

        ("ai", "['company name': ' Kielder Newport West Limited',\
        'Purchase Number': '',\
        'INVOICE NO': '1622487',\
        'Date': '09 June 2023',\
        'Sort Code': '01-01-35',\
        'Net Amount': 1,624.00,\
        'VAT @ 20%': 324.80,\
        'Total Due': 1,948.80\
        'A/C Number': ' 17887623',\
        'A/c Name': 'Kielder Newport West Ltd']"),
        ("human", "{input}"),
        ("ai", "?")])
        self.invoice_schema = {
        "properties": {
            "company name": {"type": "string"},
            "PURCHASE ORDER": {"type": "string"},
            "order No": {"type": "string"},
            "INVOICE NO": {"type": "string"},
            "Date": {"type": "string"},
            "Sort Code": {"type": "string"},
            "Net Amount": {"type": "integer"},
            "VAT @ 20%": {"type": "integer"},
            "Total Due": {"type": "integer"},
            "Account Number": {"type": "string"},
            "A/c Name": {"type": "string"},

        },
        "required": ["company name",  "INVOICE NO", "PURCHASE ORDER","order No", "Account Number", "A/c Name", "Date", "Net Total",  "VAT @ 20%", "Sort Code"],
        }
        self.invice_chain = create_extraction_chain(self.invoice_schema, llm, self.prompt_invoice)


    def _run_po_chain(self, text: str):
        return self.po_chain(text,return_only_outputs=True)
    
    def _run_invoice_chain(self, text: str):
        return self.invice_chain(text,return_only_outputs=True)
    async def __call__(self, request: Request):
        # 1. Pars the request
        pdf_data = await request.body()
        input_type = request.query_params["kind"]
        # print('-'*30)
        # print('input_typeinput_typeinput_type', input_type, type(input_type))
        pdf_file = BytesIO(pdf_data)
        import pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

        if input_type.lower() == 'po':
            resp = self._run_po_chain(text)
        elif input_type.lower() == 'invoice':
            resp = self._run_invoice_chain(text)
        else:
            resp = None
        print(resp)

        return resp




deployment = DeployLLM.bind()

PORT_NUMBER = 8003
serve.run(deployment, port=PORT_NUMBER, host="0.0.0.0")
