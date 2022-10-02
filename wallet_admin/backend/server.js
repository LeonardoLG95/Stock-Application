require("dotenv").config()
let express = require("express")
let cors = require("cors")
let bodyParser = require("body-parser")

const host = process.env.HOST
const port = process.env.PORT
const buyEndpoint = process.env.BUY_ENDPOINT
const buyList = process.env.BUY_LIST_ENDPOINT
const sellEndpoint = process.env.SELL_ENDPOINT
const sellList = process.env.SELL_LIST_ENDPOINT

// Mongo declarations
const mongoose = require("mongoose")

const Schema = mongoose.Schema
mongoose.connect(`mongodb://${host}`,
	{ useNewUrlParser: true, useUnifiedTopology: true },
	(err) => {
		if (err) console.log(err)
	})

const commonSchema = {
	_id: { type: mongoose.Schema.Types.ObjectId, auto: true },
	symbol: { type: String, required: true },
	stockPrice: { type: Number, required: true },
	quantity: { type: Number, required: true },
	usdPrice: { type: Number, required: true },
	eurPrice: { type: Number, required: true },
	operationDate: { type: Date, required: true }
}

const buySchema = new Schema(commonSchema)
const sellSchema = new Schema(commonSchema)

const BuyOperation = mongoose.model("BuyOperation", buySchema)
const SellOperation = mongoose.model("SellOperation", sellSchema)

// Express declarations
const app = express()
app.use(cors())
app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static("public"))

app.post(buyEndpoint, (req, res) => {
	console.log(req.body)
	let buy = new BuyOperation({
		symbol: req.body.data.symbol,
		stockPrice: req.body.data.stockPrice,
		quantity: req.body.data.quantity,
		usdPrice: req.body.data.usdPrice,
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
		usdPrice: req.body.data.usdPrice,
		eurPrice: req.body.data.eurPrice,
		operationDate: req.body.data.operationDate,
	})

	sell.save((err, sell) => {
		if (err) return console.error(err)
		res.json({ _id: sell._id, symbol: sell.symbol, state: "Recorded!"})
	})
})

app.get(buyList, (_, res)=> {
	BuyOperation.find().exec((err, buyOperations)=>{
		if(err) return console.log(err)
		res.json({operations: buyOperations})
	})
})

app.get(sellList, (_, res)=> {
	SellOperation.find().exec((err, sellOperations)=>{
		if(err) return console.log(err)
		res.json({operations: sellOperations})
	})
})

const listener = app.listen(port|| 3000, () => {
	console.log("Your app is listening on port " + listener.address().port)
})