import socket
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from functools import partial


class Client:

	def __init__(self):
		self.GUI = GUI(self)
		self.GUI.ConfigurateMenuUI()
		self.ServerData = ('127.0.0.1', 9080)
		self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.Socket.bind(("", 0))
	
	def SendMessage(self, message):
		self.Socket.sendto(message.encode("utf-8"), self.ServerData)
	
	def GetMessage(self):
		return self.Socket.recv(1024).decode("utf-8")
	
	def Start(self):
		self.GUI.Window.mainloop()
	
	def GetCars(self):
		self.SendMessage("/get cars")
		return json.loads(self.GetMessage())
	
	def GetOrders(self):
		self.SendMessage("/get orders")
		return json.loads(self.GetMessage())
	
	def CreateOrder(self, event):
		template = "/add {}"
		data = self.GUI.GetDataForOrder()
		data['type'] = 'order'
		self.SendMessage(template.format(json.dumps(data)))
		msg = self.GetMessage()

		if msg == "Ваш заказ успешно зарегистрирован в системе":
			self.GUI.OnTopLevelClosed()
			messagebox.showinfo("Info", msg)
	
	def RegisterCar(self, event):
		template = "/add {}"
		data = self.GUI.GetDataForCar()
		data['type'] = 'car'
		self.SendMessage(template.format(json.dumps(data)))
		msg = self.GetMessage()

		if msg == "Ваше авто успешно зарегистрировано в системе":
			self.GUI.ReloadCars()
			messagebox.showinfo("Info", msg)
class GUI:

	def __init__(self, Client: Client):
		self.Client = Client
		self.CreateWindow()
		self.CreateMenuUI()
		self.PackMenuUI()
		self.IsBlocked = False

	def CreateWindow(self):
		self.Window = tk.Tk()
		self.Window.title("Taxi sevice")

	def CreateMenuUI(self):
		self.OrderButton = tk.Button(text="Я - заказчик")
		self.OfferButton = tk.Button(text="Я - исполнитель")
		self.MenuWidgets = (self.OrderButton, self.OfferButton)
	
	def CreateTopLevelUIOrder(self):
		self.LabelOrdPhone = tk.Label(self.TopLevel, text="Ваш номер")
		self.PhoneEntry = tk.Entry(self.TopLevel)
		self.GoButton = tk.Button(self.TopLevel, text="Отправить")
		self.TopLevelWidgets = (self.CarsSelect, self.PhoneEntry, self.GoButton, self.LabelOrdCar, self.LabelOrdPhone)
	
	def CreateTopLevelUIOffer(self):
		self.CarAddButton = tk.Button(self.TopLevel, text="Моего авто нет в списке")
		self.OrdersButton = tk.Button(self.TopLevel, text="Посмотреть заказы")
		self.TopLevelWidgets = (self.CarsSelect, self.CarAddButton, self.OrdersButton)

	def PackMenuUI(self):
		for widget in self.MenuWidgets:
			widget.pack(pady=3)
	
	def PackTopLevelUI(self):
		if self.ClientType == 'order':
			self.LabelOrdPhone.grid(column=0, row=0)
			self.PhoneEntry.grid(column=1, row=0)
			self.GoButton.grid(column=1, row=2)
		elif self.ClientType == 'offer':
			self.CarAddButton.grid(column=0, row=2)
			self.OrdersButton.grid(column=1, row=2)
		else:
			return

		self.CarsSelect.grid(column=1, row=1)
		self.LabelOrdCar.grid(column=0, row=1)

	def ConfigurateMenuUI(self):
		self.Window.geometry("300x200")
		self.OrderButton.bind("<Button-1>", partial(self.CreateTopLevel, "order"))
		self.OfferButton.bind("<Button-1>", partial(self.CreateTopLevel, "offer"))
	
	def ConfigurateTopLevelUI(self):
		
		if self.ClientType == "order":
			self.GoButton.bind("<Button-1>", self.Client.CreateOrder)
		else:
			self.CarAddButton.bind("<Button-1>", self.Client.RegisterCar)
			self.OrdersButton.bind("<Button-1>", self.CreateViewer)
		
		self.TopLevel.protocol("WM_DELETE_WINDOW", self.OnTopLevelClosed)		
		self.ReloadCars()
	
	def OnTopLevelClosed(self):
		for widget in self.TopLevelWidgets:
			widget.destroy()
		self.TopLevel.destroy()
		self.IsBlocked = False
	
	def OnViewerClosed(self):
		for widget in self.ViewerWidgets:
			widget.destroy()
		self.Viewer.destroy()
		self.OrdersView = False
	
	def ReloadCars(self):
		self.Cars = self.Client.GetCars()
		Cars_strings = [f"{x['mark']} | {x['model']}" for x in self.Cars]
		self.CarsSelect['values'] = Cars_strings
		if len(self.Cars) > 0:
			self.TopLevelWidgets[0].current(0)
	
	def ReloadOrders(self):
		self.Orders = self.Client.GetOrders()
		self.OrdersCount = len(self.Orders)

		if self.OrdersCount <= 0:
			self.LabelCar['text'] = "There are no orders"
			return

		self.CurrentOrderPos = 1
	
	def CreateTopLevelUI(self, type_: str):
		if not type_ in ("offer", "order"):
			raise Exception("Bad type_ argument. Shoul be 'offer' or 'order'")

		self.CarsSelect = ttk.Combobox(self.TopLevel)
		self.LabelOrdCar = tk.Label(self.TopLevel, text="Выберите авто")
		if type_ == "offer":
			self.CreateTopLevelUIOffer()
			self.OrdersView = False
		elif type_ == "order":
			self.CreateTopLevelUIOrder()
	
	def CreateTopLevel(self, type_: str, event):
		if self.IsBlocked:
			return
		
		self.IsBlocked = True
		self.TopLevel = tk.Toplevel(self.Window)

		self.CreateTopLevelUI(type_)

		self.ClientType = type_
		self.PackTopLevelUI()
		self.ConfigurateTopLevelUI()
	
	def CreateViewerUI(self):
		self.LabelCount = tk.Label(self.Viewer, font="TimesNewRoman 14 bold")
		self.LabelCar = tk.Label(self.Viewer, font="TimesNewRoman 14")
		self.LabelPhone = tk.Label(self.Viewer, font="TimesNewRoman 14")
		self.ButtonNext = tk.Button(self.Viewer, text="→")
		self.ButtonPrev = tk.Button(self.Viewer, text="←")
		self.ViewerWidgets = (self.LabelCar, self.LabelCount, self.LabelPhone, self.ButtonNext, self.ButtonPrev)
	
	def PackViewerUI(self):
		self.LabelCar.grid(column=0, row=0)
		self.LabelPhone.grid(column=0, row=1)
		self.ButtonPrev.grid(column=0, row=2)
		self.LabelCount.grid(column=1, row=2)
		self.ButtonNext.grid(column=2, row=2)
	
	def GoToOrder(self, event, forward):
		if (forward) and (self.CurrentOrderPos == self.OrdersCount):
			self.CurrentOrderPos = 0
		elif (not forward) and (self.CurrentOrderPos == 1):
			self.CurrentOrderPos = self.OrdersCount
		
		self.CurrentOrderPos += int(forward)
		self.ShowOrder()

	def ShowOrder(self):
		order = self.Orders[self.CurrentOrderPos - 1]
		self.LabelCount["text"] = f"{self.CurrentOrderPos}/{self.OrdersCount}"
		self.LabelCar['text'] = f"{order['mark']} | {order['model']}"
		self.LabelPhone['text'] = order['phone']

	def ConfigurateViewerUI(self):
		self.ReloadOrders()
		self.ButtonNext.bind("<Button-1>", partial(self.GoToOrder, forward=True))
		self.Viewer.protocol("WM_DELETE_WINDOW", self.OnViewerClosed)		
		self.ShowOrder()
	
	def CreateViewer(self, event):
		if self.OrdersView:
			return
		
		self.OrdersView = True
		self.Viewer = tk.Toplevel(self.Window)
		self.CreateViewerUI()
		self.PackViewerUI()
		self.ConfigurateViewerUI()
	
	def GetDataForCar(self):
		mark = simpledialog.askstring("Car Mark", "Input your car mark here")
		model = simpledialog.askstring("Car Model", "Input your car model here")
		car = {
			'mark': mark,
			'model': model
		}

		return car

	def GetDataForOrder(self):
		mark, model = self.CarsSelect.get().split(" | ")
		phone = self.PhoneEntry.get()

		order = {
			'mark': mark,
			'model': model,
			'phone': phone
		}

		return order
