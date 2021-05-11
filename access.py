from optionchain_stream import OptionChain


if __name__ == "__main__":
	OptionStream = OptionChain("ydq5afgjqoqvj0up", "mlwdiwz24dnwpsu9jtozht4n4c5zncjb", "b24RIKYeP4Ym5aiwB3NNV3d23xhNJpxn",
                    "ITC", "2021-05-27")#SBIN

	# OptionStream.sync_instruments() #51091) "24275970"

	StreamData = OptionStream.create_option_chain() #51213)
	# for data in StreamData:
	# 	print(data)

	print("Imported!")