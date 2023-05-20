# -*- coding: utf-8 -*-
"""Projet SQL - Toys and Models.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hDIXcA-lsUoM8Rr0cqRxVA9IbBoU4GFj
"""

# Sales : nombre de pdts vendus / cat et / mois + Comparaison et tx de var du meme mois de l’année N - 1
# Code Sales avec les pays
select *,
(NombreArticlesCommandes - LagNombreArticleCommande) as  difference,
((NombreArticlesCommandes - LagNombreArticleCommande) / LagNombreArticleCommande) as division
from
	(select *, 
	lag(NombreArticlesCommandes,1,0) over (partition by categorie, mois order by categorie,mois,annee) as LagNombreArticleCommande
	from
		(select  products.productLine as categorie, 
				year(orders.orderDate) as annee,
				monthname(orders.orderDate) as mois,
                customers.country as Pays,
				sum(orderdetails.quantityOrdered) as NombreArticlesCommandes
		from customers
        inner join orders on orders.customerNumber = customers.customerNumber
		inner join orderdetails on orders.orderNumber = orderdetails.orderNumber 
		inner join products on products.productCode = orderdetails.productCode
		group by productLine,annee,mois, Pays) as TabDeBase
        ) as TabPlusLag

# Logistics : Kpi des 5 produits les plus commandés
select * from (
select  products.productCode, sum(orderdetails.quantityOrdered ) AS Quantity_ordered_by_product, products.productName,
RANK() OVER   
    (ORDER BY sum(orderdetails.quantityOrdered ) DESC)  as TOP5, (products.quantityInStock) 
from orders 
inner join orderdetails on orders.orderNumber = orderdetails.orderNumber 
inner join products on products.productCode = orderdetails.productCode
group by products.productCode) sub 
where TOP5 between 1 and 5;

# Finance : CA des commandes des 2 derniers mois par pays
# 2021
select *,
	(ca - achat) as profits
from
(select 
	customers.country,
	date_format(orders.orderDate, "%Y/%m") as mois , 
    sum(orderdetails.quantityOrdered*orderdetails.priceEach) as ca,
    round(sum(products.buyPrice*orderdetails.quantityOrdered)) as achat
from products
join orderdetails on orderdetails.productCode = products.productCode
join orders on orders.orderNumber  = orderdetails.orderNumber
join customers on customers.customerNumber = orders.customerNumber
where date_format(orders.orderDate, "%Y/%m")  between '21/01' and '21/12'
group by customers.country, date_format(orders.orderDate, "%Y/%m")) sub
order by country;

# 2022
select *,
	(ca - achat) as profits
from
(select 
	customers.country,
	date_format(orders.orderDate, "%Y/%m") as mois , 
    sum(orderdetails.quantityOrdered*orderdetails.priceEach) as ca,
    round(sum(products.buyPrice*orderdetails.quantityOrdered)) as achat
from products
join orderdetails on orderdetails.productCode = products.productCode
join orders on orders.orderNumber  = orderdetails.orderNumber
join customers on customers.customerNumber = orders.customerNumber
where date_format(orders.orderDate, "%Y/%m")  between '21/01' and '21/12'
group by customers.country, date_format(orders.orderDate, "%Y/%m")) sub
order by country;

# les commandes impayées par pays et compagnie
select Client, Pays, MontantDeLaCommande as MontantDeLaCommandeInitial,
MontantCommandeAnnule,
MontantDeLaCommande - MontantCommandeAnnule as MontantCommandeReel, 
MontantPaye,
MontantDeLaCommande - MontantCommandeAnnule - MontantPaye as MontantImpayé, 
case when  MontantDeLaCommande - MontantCommandeAnnule - MontantPaye > 0 then 'Impayé'
	when MontantDeLaCommande - MontantCommandeAnnule - MontantPaye < 0 then 'SurplusPaiement' 
		else 'Payé' end as FlagImpaye 
from(
with A as (
select sum(orderdetails.quantityOrdered*orderdetails.priceEach) as MontantDeLaCommande,
customers.customerName as Client,
customers.country as Pays
from orderdetails 	 
inner join orders  on orderdetails.orderNumber = orders.orderNumber
inner join customers  on customers.customerNumber = orders.customerNumber
group by  orders.customerNumber
),
B as (
select sum(amount) as MontantPaye, customers.customerName
from payments 
inner join customers  on payments.customerNumber = customers.customerNumber
group by customers.customerName
),
C as (
select sum(case when status = 'Cancelled' then orderdetails.quantityOrdered *orderdetails.priceEach else 0 end) as MontantCommandeAnnule,  customerName as NomClient2 
from  orders 
inner join orderdetails on orders.orderNumber = orderdetails.orderNumber
inner join customers  on customers.customerNumber = orders.customerNumber
group by  customerName)
select * from A
inner join B on A.Client = B.customerName
inner join C on B.customerName = C.NomClient2) as tab
order by FlagImpaye;

# HR : Chaque mois les 2 vendeurs avec le CA le + élevé avec ajout de la marge brute
select *, (ca - achat) as profits 
from (
select * from (
select 
		rank() over(partition by date_format(orders.orderDate, "%y/%m") order by sum(orderdetails.quantityOrdered*priceEach) DESC) as top2,
		employees.firstName, 
		employees.lastName, 
        date_format(orders.orderDate, "%y/%m") as mois, 
        sum(orderdetails.quantityOrdered*priceEach) as ca,
        round(sum(products.buyPrice*orderdetails.quantityOrdered)) as achat
from products
inner join orderdetails on orderdetails.productCode = products.productCode
inner join orders on orders.orderNumber = orderdetails.orderNumber 
inner join customers on customers.customerNumber =orders.customerNumber 
inner join employees on customers.salesRepEmployeeNumber = employees.employeeNumber
group by employees.firstName, employees.lastName, date_format(orders.orderDate, "%y/%m")) subsub ) subplus
where top2 in (1,2)
order by mois desc, ca desc;

# Top 5 des des produits les plus rentables
select *,(ca - achat) as profits from (
select  products.productCode, products.productName,
RANK() OVER   
    (ORDER BY sum(orderdetails.quantityOrdered * orderdetails.priceEach  ) DESC)  as TOP10, 
round(sum(orderdetails.quantityOrdered * orderdetails.priceEach)) as ca, 
round(sum(products.buyPrice*orderdetails.quantityOrdered)) as achat
from orders 
inner join orderdetails on orders.orderNumber = orderdetails.orderNumber 
inner join products on products.productCode = orderdetails.productCode
group by products.productCode) sub 
where TOP10 between 1 and 10;

# Top marge par pays
select *,(ca - achat) as profits from (
select  
	products.productCode, 
    products.productName,
    orders.orderDate,
    customers.country,
	RANK() OVER   
		(ORDER BY (ca - achat) DESC) as TOP, 
round(sum(orderdetails.quantityOrdered * orderdetails.priceEach)) as ca, 
round(sum(products.buyPrice*orderdetails.quantityOrdered)) as achat
from customers
inner join orders on orders.customerNumber = customers.customerNumber
inner join orderdetails on orders.orderNumber = orderdetails.orderNumber 
inner join products on products.productCode = orderdetails.productCode
group by products.productCode, products.productName, orders.orderDate, customers.country) sub 
;