import boto3
from reportlab.pdfgen import canvas

start = input("Enter start date (YYYY-MM-DD): ")
end = input("Enter end date (YYYY-MM-DD): ")

ce = boto3.client("ce", region_name="us-east-1")

data = ce.get_cost_and_usage(
    TimePeriod={"Start": start, "End": end},
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
)

total = 0
services = {}
daily = {}

for day in data["ResultsByTime"]:
    date = day["TimePeriod"]["Start"]
    daily[date] = 0

    for group in day["Groups"]:
        service = group["Keys"][0]
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        currency = group["Metrics"]["UnblendedCost"]["Unit"]

        total += cost
        daily[date] += cost
        services[service] = services.get(service, 0) + cost

print("Billing Period:", start, "to", end)
print("Total AWS Cost:", round(total, 2), currency)

print("\nService-wise Costs:")
for service, cost in services.items():
    print(service, ":", round(cost, 2), currency)

print("\nDaily Costs:")
for date, cost in daily.items():
    print(date, ":", round(cost, 2), currency)

pdf = canvas.Canvas("aws_billing_report.pdf")

pdf.drawString(50, 800, "AWS Billing Report")
pdf.drawString(50, 780, f"Billing Period: {start} to {end}")
pdf.drawString(50, 760, f"Total AWS Cost: {total:.2f} {currency}")
pdf.drawString(50, 740, f"Currency: {currency}")

y = 700
pdf.drawString(50, y, "Service-wise Costs:")
y -= 20

for service, cost in services.items():
    pdf.drawString(60, y, f"{service}: {cost:.2f} {currency}")
    y -= 20

y -= 20
pdf.drawString(50, y, "Daily Costs:")
y -= 20

for date, cost in daily.items():
    pdf.drawString(60, y, f"{date}: {cost:.2f} {currency}")
    y -= 20

pdf.save()

print("PDF report generated successfully.")