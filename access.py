from optionchain_stream import OptionChain


if __name__ == "__main__":
	OptionStream = OptionChain("<api-key-here>", "<api-secret-here>", "<acess-token-here>",
                    "ITC", "2021-05-27")

	OptionStream.sync_instruments() #Uncomment once

	StreamData = OptionStream.create_option_chain() #51213)
	for data in StreamData:
		print(data)

	print("Imported!")