require("dotenv").config()
let express = require("express")
let cors = require("cors")
let bodyParser = require("body-parser")

const db_host = process.env.DB_HOST
const puller_host = process.env.PULLER_HOST
const port = process.env.PORT
const buyEndpoint = process.env.BUY_ENDPOINT
const buyList = process.env.BUY_LIST_ENDPOINT
const sellEndpoint = process.env.SELL_ENDPOINT
const sellList = process.env.SELL_LIST_ENDPOINT
const deleteBuyEndpoint = process.env.DELETE_BUY_ENDPOINT
const deleteSellEndpoint = process.env.DELETE_SELL_ENDPOINT
const walletEvolutionEndpoint = process.env.WALLET_EVOLUTION_ENDPOINT

// Mongo declarations
const mongoose = require("mongoose")

const Schema = mongoose.Schema
mongoose.connect(`mongodb://${db_host}`,
	{ useNewUrlParser: true, useUnifiedTopology: true },
	(err) => {
		if (err) console.log(err)
	})

const commonSchema = {
	_id: { type: mongoose.Schema.Types.ObjectId, auto: true },
	symbol: { type: String, required: true },
	stockPrice: { type: Number, required: true },
	quantity: { type: Number, required: true },
	eurPrice: { type: Number, required: true },
	operationDate: { type: Date, required: true }
}

const buySchema = new Schema(commonSchema)
const sellSchema = new Schema(commonSchema)

const BuyOperation = mongoose.model("BuyOperation", buySchema)
const SellOperation = mongoose.model("SellOperation", sellSchema)

// Express declarations
const app = express()
app.use(cors({
	origin: '*'
}))
app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static("public"))

app.post(buyEndpoint, (req, res) => {
	let buy = new BuyOperation({
		symbol: req.body.data.symbol,
		stockPrice: req.body.data.stockPrice,
		quantity: req.body.data.quantity,
		eurPrice: req.body.data.eurPrice,
		operationDate: req.body.data.operationDate,
	})

	buy.save((err, buy) => {
		if (err) return console.error(err)
		res.json({ _id: buy._id, symbol: buy.symbol, buy: "Recorded!" })
	})
})

app.post(sellEndpoint, (req, res) => {
	let sell = new SellOperation({
		symbol: req.body.data.symbol,
		stockPrice: req.body.data.stockPrice,
		quantity: req.body.data.quantity,
		eurPrice: req.body.data.eurPrice,
		operationDate: req.body.data.operationDate,
	})

	sell.save((err, sell) => {
		if (err) return console.error(err)
		res.json({ _id: sell._id, symbol: sell.symbol, state: "Recorded!" })
	})
})

app.get(buyList, (_, res) => {
	BuyOperation.find().exec((err, buyOperations) => {
		if (err) return console.log(err)
		res.json({ operations: buyOperations })
	})
})

app.get(sellList, (_, res) => {
	SellOperation.find().exec((err, sellOperations) => {
		if (err) return console.log(err)
		res.json({ operations: sellOperations })
	})
})

app.post(deleteBuyEndpoint, (req, res) => {
	BuyOperation.deleteOne({ _id: req.body.data._id }, (err, operation) => {
		if (err) return console.log(err)
		res.json({ result: `Operation deleted!` })
	})
})

app.post(deleteSellEndpoint, (req, res) => {
	SellOperation.deleteOne({ _id: req.body.data._id }, (err, operation) => {
		if (err) return console.log(err)
		res.json({ result: `Operation deleted!` })
	})
})

app.post(walletEvolutionEndpoint, async (req, res) => {
	async function getHistoryForBuyOperations(buyOperations) {
		async function getPrices(symbol, start_operation, end_operation, resolution) {
			let prices = await fetch(`http://${puller_host}:8000/symbol_prices`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ symbol, start_operation, end_operation, resolution: resolution })
			})
				.then(response => response.json())
				.then(data => data.response)

			return { [symbol]: prices }
		}

		let buyHistory = {}
		for (let b of buyOperations) {
			let end_date = null

			// Not valid if you don't sell all
			for (let s of sellOperations) {
				if (s.symbol === b.symbol) {
					end_date = s.operationDate
					break
				}
			}
			buyHistory = Object.assign({}, await getPrices(b.symbol, b.operationDate, end_date, resolution), buyHistory)
		}
		return buyHistory
	}

	function calculateHistoryInOperations(buyOperations, buyHistory, sellOperations) {
		// Calculate movements * quantity of stocks

		let walletEvolutionRaw = []
		for (let i = 0; i < buyOperations.length; i++) {
			let operation = buyOperations[i]
			let symbol = operation.symbol
			let quantity = operation.quantity

			if (buyHistory[symbol] === null) {
				walletEvolutionRaw.push([new Date(operation.operationDate), operation.stockPrice * quantity])
				continue
			}

			symbolHistory = []
			for (let f = 0; f < buyHistory[symbol].length; f++) {
				let date = new Date(buyHistory[symbol][f][0])

				let sold = false
				// To avoid last date repetition
				if (f + 1 < buyHistory[symbol].length) {
					let next_date = new Date(buyHistory[symbol][f + 1][0])
					if (date.getMonth() === next_date.getMonth()) {
						continue
					}
				}
				else { //Take sell price in the last point, not valid if you don't sell all
					for (let s of sellOperations) {
						if (s.symbol === symbol) {
							symbolHistory.push([date, s.stockPrice * s.quantity])
							sold = true
							break
						}
					}
					if (sold) break
				}

				symbolHistory.push([date, buyHistory[symbol][f][1] * quantity])
			}
			walletEvolutionRaw = walletEvolutionRaw.concat(symbolHistory)
		}
		return walletEvolutionRaw
	}

	function calculateWalletEvolution(walletEvolutionRaw) {
		let walletEvolution = []

		let month = null
		let date = null
		let value = null

		for (let i = 0; i < walletEvolutionRaw.length; i++) {
			let rowMonth = walletEvolutionRaw[i][0].getMonth()

			// Group by month
			if (month !== rowMonth || i + 1 == walletEvolutionRaw.length) {
				month = rowMonth

				if (value !== null) {
					walletEvolution.push([date, value])
				}
				date = walletEvolutionRaw[i][0]
				value = walletEvolutionRaw[i][1]
				continue
			}

			value += walletEvolutionRaw[i][1]
		}

		return walletEvolution
	}

	function parseDatesForChart(walletEvolution) {
		for (let i = 0; i < walletEvolution.length; i++) {
			const pad = (s) => { return (s < 10) ? '0' + s : s }
			let date = walletEvolution[i][0]
			walletEvolution[i][0] = [pad(date.getDate()), pad(date.getMonth() + 1), date.getFullYear()].join('-')
		}

		return walletEvolution
	}

	// Request info
	let resolution = req.body.resolution
	let buyOperations = req.body.buyOperations
	let sellOperations = req.body.sellOperations

	let buyHistory = await getHistoryForBuyOperations(buyOperations)
	let walletEvolutionRaw = calculateHistoryInOperations(buyOperations, buyHistory, sellOperations)

	// Sort array
	walletEvolutionRaw.sort((a, b) => {
		return (new Date(a[0])).getTime() - (new Date(b[0])).getTime();
	})

	walletEvolution = calculateWalletEvolution(walletEvolutionRaw)
	walletEvolution = parseDatesForChart(walletEvolution)


	// console.log(walletEvolution)
	res.json({ result: walletEvolution }) // Missing sells
})

const listener = app.listen(port || 3000, () => {
	console.log("Your app is listening on port " + listener.address().port)
})