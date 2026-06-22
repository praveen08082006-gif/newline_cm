from django.db import migrations

PRODUCTS = [
    "Pentouch PTw65 (M22)",
    "Pentouch PTw65 (M24)",
    "Pentouch PTw75 (M24)",
    "Pentouch PTw86 (M22)",
    "S 65",
    "S 75",
    "S 86",
    "SRX900 (i7)",
    "STV - 4324",
    "STV - 5524",
    "STV - 6524",
    "STV - 7524",
    "STV - 8524",
    "STV - 9824",
    "TT-2721AIO (FLEX)",
    "TT-5521Q",
    "TT-5522Z",
    "TT-5523QA ( TT-5524QPRO)",
    "TT-6518RS",
    "TT-6519RS",
    "TT-6520ER ATLAS 65",
    "TT-6520HO Mira 65",
    "TT-6521Q",
    "TT-6522S",
    "TT-6523QA ( TT-6524QPRO)",
    "TT-6523S ( SPRO)",
    "TT-6524Z PRO",
    "TT-7518RS+",
    "TT-7519I",
    "TT-7519RS",
    "TT-7520ER ATLAS 75",
    "TT-7521Q",
    "TT-7522Q",
    "TT-7522S",
    "TT-7522Z",
    "TT-7523QA ( TT-7524QPRO)",
    "TT-7523QCA+",
    "TT-7523S ( SPRO)",
    "TT-7524M ( MPRO - OEM)",
    "TT-7524Z PRO",
    "TT-8618RS+",
    "TT-8619RS",
    "TT-8620HO MIRA 86",
    "TT-8621Q",
    "TT-8622S",
    "TT-8622Z",
    "TT-8623QA ( TT-8624QPRO)",
    "TT-8623QCA+",
    "TT-8623S ( SPRO)",
    "TT-8624M ( MPRO - OEM)",
    "TT-9819NT",
    "TT-9821Q",
    "TT-9823QA (TT-7524QPRO)",
    "TWB-6523A",
    "TWB-6524AI",
    "TWB-6524M",
    "TWB-7522M",
    "TWB-7523A",
    "TWB-7524AI",
    "TWB-7524M",
    "TWB-8622M",
    "WB5A118W",
    "WB5A120W",
    "WB5A131W",
    "WB5A132W",
    "WB5A135W",
    "WB5A136W",
    "WB5A137W",
    "WB7WB120W",
    "WBSRX800",
    "X5",
    "X7",
    "X8",
]


def seed_products(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    for name in PRODUCTS:
        Product.objects.get_or_create(name=name)


def unseed_products(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    Product.objects.filter(name__in=PRODUCTS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_complaint_serial_number'),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
