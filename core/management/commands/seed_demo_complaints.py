"""
Seed demo complaints spread across many products so the dashboard charts
look full for demos / screenshots.

    python manage.py seed_demo_complaints            # add ~150 demo complaints
    python manage.py seed_demo_complaints --count 200
    python manage.py seed_demo_complaints --clear    # remove only the demo data

Demo complaints are tagged with customer_email = "demo@newline.local" so
--clear removes exactly these and nothing else.
"""
import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Complaint, Employee, Product, REGION_CHOICES

DEMO_EMAIL = "demo@newline.local"

REGIONS = [r[0] for r in REGION_CHOICES]

STATUSES = (
    ['Resolved'] * 8 + ['In Progress'] * 5 + ['Replaced'] * 2 +
    ['Reopen'] * 2 + ['Case Locked'] * 2 + ['Abort'] * 1 +
    ['Workshop attention/Repair'] * 1 + ['Not Responded Calls'] * 1 +
    ['Resolved after panel Replacement'] * 1
)
RESOLVED = {'Resolved', 'Replaced', 'Resolved after panel Replacement'}

FIRST = ['Praveen', 'Anita', 'Rahul', 'Sneha', 'Vijay', 'Meera', 'Arjun', 'Divya',
         'Karthik', 'Pooja', 'Suresh', 'Lakshmi', 'Imran', 'Neha', 'Rohit', 'Fatima',
         'Sanjay', 'Priya', 'Gopal', 'Ananya']
LAST = ['Kumar', 'Sharma', 'Reddy', 'Nair', 'Iyer', 'Patel', 'Singh', 'Das',
        'Menon', 'Rao', 'Khan', 'Pillai', 'Joshi', 'Verma', 'Gupta']
TYPES = ['Display Issue', 'Touch Not Working', 'No Power', 'Software', 'Android OS',
         'Camera', 'Speaker', 'OPS / PC', 'Installation', 'Warranty Claim']
DISTRIBUTORS = ['Apex Systems', 'TechVision', 'DigiWorld', 'ClearView Solutions',
                'NextGen Traders', 'Bright Displays', 'Unity Infotech', '']


class Command(BaseCommand):
    help = "Add demo complaints across many products (or --clear to remove them)."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=150,
                            help='How many demo complaints to create (default 150).')
        parser.add_argument('--products', type=int, default=16,
                            help='How many distinct products appear in the chart (default 16).')
        parser.add_argument('--clear', action='store_true',
                            help='Delete demo complaints instead of creating them.')

    def handle(self, *args, **opts):
        if opts['clear']:
            n, _ = Complaint.objects.filter(customer_email=DEMO_EMAIL).delete()
            self.stdout.write(self.style.SUCCESS(f"Removed demo complaints ({n} rows)."))
            return

        products = list(Product.objects.all())
        if not products:
            self.stdout.write(self.style.ERROR("No products found. Run migrate first."))
            return

        creator = User.objects.filter(is_superuser=True).first() or User.objects.first()
        # group SPOC employees by region for realistic assignment
        emps_by_region = {}
        for e in Employee.objects.all():
            emps_by_region.setdefault(e.region, []).append(e)

        # use a wide spread of products so the chart shows many slices
        count = opts['count']
        pool = products[:]
        random.shuffle(pool)
        # keep the chart full but readable: a fixed set of distinct products
        spread = pool[:min(len(pool), opts['products'])]

        created = 0
        for _ in range(count):
            product = random.choice(spread)
            region = random.choice(REGIONS)
            status = random.choice(STATUSES)
            reg = date.today() - timedelta(days=random.randint(0, 150))
            spoc = None
            if emps_by_region.get(region):
                spoc = random.choice(emps_by_region[region])

            c = Complaint(
                product=product,
                serial_number=f"NL{random.randint(10000, 99999)}",
                customer_name=f"{random.choice(FIRST)} {random.choice(LAST)}",
                customer_mobile=f"9{random.randint(100000000, 999999999)}",
                customer_email=DEMO_EMAIL,
                complaint_type=random.choice(TYPES),
                spoc=spoc,
                distributor_partner=random.choice(DISTRIBUTORS),
                distributor_mobile=f"8{random.randint(100000000, 999999999)}",
                region=region,
                country='India',
                status=status,
                description="[DEMO] Sample complaint for dashboard demonstration.",
                registration_date=reg,
                created_by=creator,
            )
            # realistic closed_date for resolved ones (a few days after registration)
            if status in RESOLVED:
                c.closed_date = reg + timedelta(days=random.randint(1, 12))
            c.save()
            created += 1

        distinct = len({p.id for p in spread})
        self.stdout.write(self.style.SUCCESS(
            f"Created {created} demo complaints across {distinct} products."))
