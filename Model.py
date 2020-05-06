Class Order(object):
	def __init__(self,supplier):
		#object of class supplier
		self.supplier
		#fixed cost of the supplier
		self.fixed_cost=self.supplier.fixed_cost
		#ordered items from supplier
		self.items={
			"mele":3 #num di kg di ganja ordinate
			"banane":10
		}
		#time to arrive
		self.time_to_arrive
		#discount depending on the supplier
		self.discount=supplier.discount(n_of_items)
		#total cost of the order
		self.total_cost=self.fixed_cost
		for item in self.items:
			item_cost=self.supplier.available_products[item.key] # supplier.getPrice(item)
			self.total_cost+=item.value*item_cost
		self.total_cost-=self.discount

Class Supplier(object):
	def __init__(self,supplierID,available_products):
		self.supplierID=supplierID
		self.fixed_cost
		self.available_products={
			"LSD":1.9, # costo di una banana dal supplier
			"MDMA":2.7,
			"ganja":3
		}
	def Discount(self,n_of_items):
		return disc
	def getPrice(self,item):
		return price

if __name__=='__main__':
	day=0
	listino_prezzi={
		"mele":2
		"pere":3
		"nespole":3.5
		"ciliege":4.5
		"banane":3
		"arance":2.5
		"pesche":4
	}
	inventory={
		"arance":4
		"pere":5
		"mele":2
	}
	suppliers=[]
	supp1=Supplier("Mercato Centrale")
	suppliers.append(supp1)
	supp2=Supplier("Import Spagna")
	suppliers.append(supp2)
	supp3=Supplier("Frutta srl")
	suppliers.append(supp3)
	supp4=Supplier("Coltivatori diretti")
	suppliers.append(supp4)
	while day<100:
		if order_comes:
			AggiornaInventario(order)
		# NOT OUR PROBLEM HOW TO ESTIMATE DEMAND
		demand_estimation={
			"arance":2
			"banane":5
			"ciliege":2
			"mele":6
		}
		orders=Optimize(demand_estimation,suppliers)
		day+=1




