class Validator(object):

	@staticmethod
	def validateBlog(dataString):
		caseIsNotFound = True
		caseStrings = ["<script>", "<button>", "<form>", "<input>"]
		for caseString in caseStrings:
			if(dataString.find(caseString) != -1):
				caseIsNotFound = False
		return caseIsNotFound