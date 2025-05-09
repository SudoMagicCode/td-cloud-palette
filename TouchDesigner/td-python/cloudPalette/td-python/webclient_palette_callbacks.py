# me - this DAT.
# webClientDAT - The connected Web Client DAT
# statusCode - The status code of the response, formatted as a dictionary with two key-value pairs: 'code', 'message'.
# headerDict - The header of the response from the server formatted as a dictionary. Only sent once when streaming.
# data - The data of the response
# id - The request's unique identifier

def onConnect(webClientDAT, id):
	return
	
def onDisconnect(webClientDAT, id):
	return

def onResponse(webClientDAT, statusCode, headerDict, data, id):
	parent.tool.Parse_cloud_response(headerDict = headerDict, data=data)
	return
	