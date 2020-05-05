Class Order(object):
	def __init__(self,supplier):
		#object of class supplier
		self.supplier
		#fixed cost of the supplier
		self.fixed_cost=self.supplier.fixed_cost
		#ordered items from supplier
		self.items={
			"ganja":3 #num di kg di ganja ordinate
			"fumo":10
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
		"ganja":15
		"fumo afghano":12
		"fumo copertone":5
		"MDMA":30
		"chrystal meth":40
		"popper":25
		"LSD":15
	}
	inventory={
		"chrystal meth":2
		"ganja":5
		"MDMA":2
		"LSD":6
	}
	suppliers=[]
	supp1=Supplier("don Miura")
	suppliers.append(supp1)
	supp2=Supplier("don Ciruzzo")
	suppliers.append(supp2)
	supp3=Supplier("Pablo Escobar")
	suppliers.append(supp3)
	supp4=Supplier("gang di Bogotà")
	suppliers.append(supp4)
	supp5=Supplier("El Chapo")
	suppliers.append(supp5)
	supp6=Supplier("Tony lo Smilzo")
	suppliers.append(supp6)
	while day<100:
		if order_comes:
			AggiornaInventario(order)
		# NOT OUR PROBLEM HOW TO ESTIMATE DEMAND
		demand_estimation={
			"ganja":2
			"fumo afghano":5
			"MDMA":2
			"coca":6
		}
		orders=Optimize(demand_estimation,suppliers)
		day+=1




