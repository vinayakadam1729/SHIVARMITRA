from sqlalchemy.orm import Session
from app.models import Category, Product, AdminUser
from app.auth import hash_password
from app.config import settings

def seed_database(db: Session):
    """Seed initial categories, products, and admin user if empty."""
    
    # 1. Seed Admin User
    admin = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
    if not admin:
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name=settings.OWNER_NAME,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"[*] Admin user created: {settings.ADMIN_USERNAME}")

    # 2. Seed Categories
    if db.query(Category).count() == 0:
        categories_data = [
            {
                "slug": "seeds",
                "name_en": "Seeds",
                "name_mr": "बियाणे (Seeds)",
                "name_hi": "बीज (Seeds)",
                "icon": "sprout",
                "image_url": "https://images.unsplash.com/photo-1599818816827-0fa095aebbf1?w=500&auto=format&fit=crop&q=60",
                "display_order": 1
            },
            {
                "slug": "fertilizers",
                "name_en": "Fertilizers",
                "name_mr": "खते (Fertilizers)",
                "name_hi": "उर्वरक (Fertilizers)",
                "icon": "flask-conical",
                "image_url": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=500&auto=format&fit=crop&q=60",
                "display_order": 2
            },
            {
                "slug": "pesticides",
                "name_en": "Crop Protection",
                "name_mr": "कीटकनाशके आणि औषधे",
                "name_hi": "कीटनाशक एवं दवाइयां",
                "icon": "shield-check",
                "image_url": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=500&auto=format&fit=crop&q=60",
                "display_order": 3
            },
            {
                "slug": "equipment",
                "name_en": "Tools & Equipment",
                "name_mr": "कृषी अवजारे आणि यंत्रे",
                "name_hi": "कृषि उपकरण व औजार",
                "icon": "wrench",
                "image_url": "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=500&auto=format&fit=crop&q=60",
                "display_order": 4
            },
            {
                "slug": "irrigation",
                "name_en": "Irrigation Systems",
                "name_mr": "सिंचन व तुषार साधने",
                "name_hi": "सिंचाई उपकरण",
                "icon": "droplets",
                "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=500&auto=format&fit=crop&q=60",
                "display_order": 5
            },
            {
                "slug": "organic",
                "name_en": "Organic Farming",
                "name_mr": "सेंद्रिय शेती उत्पादने",
                "name_hi": "जैविक कृषि उत्पाद",
                "icon": "leaf",
                "image_url": "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?w=500&auto=format&fit=crop&q=60",
                "display_order": 6
            }
        ]
        
        category_map = {}
        for c in categories_data:
            cat_obj = Category(**c)
            db.add(cat_obj)
            db.flush()
            category_map[c["slug"]] = cat_obj.id
        db.commit()
        print("[*] Categories seeded successfully.")
    else:
        category_map = {c.slug: c.id for c in db.query(Category).all()}

    # 3. Seed Products
    if db.query(Product).count() == 0:
        products_data = [
            # Seeds
            {
                "slug": "mahyco-cotton-seeds-hybrid",
                "name_en": "Mahyco BG-II Hybrid Cotton Seeds",
                "name_mr": "माहिको बीजी-२ संकरित कापूस बियाणे",
                "name_hi": "माहिको बीजी-२ हाइब्रिड कपास बीज",
                "description_en": "High yielding, pest-resistant hybrid cotton seeds suitable for black and loamy soils of Maharashtra. High boll retention and drought tolerance.",
                "description_mr": "महाराष्ट्रातील काळ्या व मध्यम जमिनीसाठी उत्कृष्ट उत्पादनक्षम, बोंडअळी प्रतिबंधक संकरित कापूस बियाणे. भरपूर बोंडे आणि उत्तम धागा प्रत.",
                "description_hi": "उच्च पैदावार देने वाला, कीट प्रतिरोधी हाइब्रिड कपास बीज। सूखे से लड़ने की क्षमता और अधिक टिंडे।",
                "category_id": category_map["seeds"],
                "price": 864.0,
                "original_price": 950.0,
                "discount_percent": 9,
                "unit_en": "475g Packet",
                "unit_mr": "४७५ ग्रॅम पाकीट",
                "unit_hi": "४७५ ग्राम पैकेट",
                "stock_quantity": 120,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=600&auto=format&fit=crop&q=80",
                "badge": "Top Seller",
                "rating": 4.9,
                "reviews_count": 48,
                "is_featured": True
            },
            {
                "slug": "pioneer-corn-seeds-3355",
                "name_en": "Pioneer Hybrid Maize (Corn) Seeds P-3355",
                "name_mr": "पायोनिअर संकरित मका बियाणे P-3355",
                "name_hi": "पायनियर हाइब्रिड मक्का बीज P-3355",
                "description_en": "Premium quality hybrid corn seeds. Uniform ear development, orange-yellow lustrous grains, and heavy biomass suitable for grain and fodder.",
                "description_mr": "उत्कृष्ट दर्जाचे संकरित मका बियाणे. एकसमान भरलेली कणसे, चमकदार पिवळे-नारंगी दाणे आणि दाणा व चाऱ्यासाठी उत्तम.",
                "description_hi": "सर्वोत्तम गुणवत्ता वाला संकरित मक्का बीज। एक समान भुट्टे और चमकदार दाने।",
                "category_id": category_map["seeds"],
                "price": 1450.0,
                "original_price": 1600.0,
                "discount_percent": 10,
                "unit_en": "4 Kg Bag",
                "unit_mr": "४ किलो बॅग",
                "unit_hi": "४ किग्रा थैला",
                "stock_quantity": 85,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600&auto=format&fit=crop&q=80",
                "badge": "High Yield",
                "rating": 4.8,
                "reviews_count": 32,
                "is_featured": True
            },
            {
                "slug": "soybean-js-335-seeds",
                "name_en": "Certified Soybean JS-335 Seeds",
                "name_mr": "प्रमाणित सोयाबीन बियाणे जे.एस. ३३५",
                "name_hi": "प्रमाणित सोयाबीन बीज जे.एस. ३३५",
                "description_en": "Government certified JS-335 soybean seeds with over 90% germination rate. Resistant to pod shattering and quick maturing (95-100 days).",
                "description_mr": "शासकीय प्रमाणित जे.एस. ३३५ सोयाबीन बियाणे, ९०%+ उगवण क्षमता. शेंगा न तडकणारा आणि ९५-१०० दिवसांत येणारा विश्वासू वाण.",
                "description_hi": "९०% से अधिक अंकुरण क्षमता वाला प्रमाणित सोयाबीन बीज। फली चटकने से मुक्त और जल्दी पकने वाला।",
                "category_id": category_map["seeds"],
                "price": 2850.0,
                "original_price": 3100.0,
                "discount_percent": 8,
                "unit_en": "30 Kg Bag",
                "unit_mr": "३० किलो पोते",
                "unit_hi": "३० किग्रा बोरी",
                "stock_quantity": 40,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1599818816827-0fa095aebbf1?w=600&auto=format&fit=crop&q=80",
                "badge": "Certified",
                "rating": 4.7,
                "reviews_count": 64,
                "is_featured": False
            },

            # Fertilizers
            {
                "slug": "iffco-19-19-19-npk-soluble",
                "name_en": "IFFCO 100% Water Soluble NPK 19:19:19",
                "name_mr": "इफ्को १००% पाण्यात विद्राव्य खत १९:१९:१९",
                "name_hi": "इफको १००% जल विलेय उर्वरक १९:१९:१९",
                "description_en": "Fully water-soluble balanced NPK fertilizer for drip irrigation and foliar spray. Boosts vegetative growth, root expansion, and crop vigor.",
                "description_mr": "ठिबक सिंचन आणि फवारणीसाठी १००% पाण्यात विद्राव्य समतोल खत. पिकांची जोमदार वाढ आणि मुळांचा जलद विस्तार होतो.",
                "description_hi": "ड्रिप और स्प्रे के लिए १००% पानी में घुलनशील संतुलित खाद। फसलों के संपूर्ण विकास के लिए सर्वोत्तम।",
                "category_id": category_map["fertilizers"],
                "price": 180.0,
                "original_price": 220.0,
                "discount_percent": 18,
                "unit_en": "1 Kg Pack",
                "unit_mr": "१ किलो पॅक",
                "unit_hi": "१ किग्रा पैक",
                "stock_quantity": 250,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=600&auto=format&fit=crop&q=80",
                "badge": "Popular",
                "rating": 4.9,
                "reviews_count": 95,
                "is_featured": True
            },
            {
                "slug": "mahatej-micronutrient-mixture",
                "name_en": "MahaTej Chelated Micronutrient Grade II",
                "name_mr": "महातेज चिलेटेड सूक्ष्म अन्नद्रव्य ग्रेड २",
                "name_hi": "महातेज चिलेटेड सूक्ष्म पोषक तत्व ग्रेड २",
                "description_en": "Essential blend of Zinc, Ferrous, Manganese, Copper, Boron and Molybdenum to cure yellowing of leaves and boost flowering.",
                "description_mr": "झिंक, फेरस, बोरॉन, कॉपर, मॅग्नेशियमचे समृद्ध मिश्रण. पिकांचा पिवळेपणा दूर करून फुले व फळधारणा वाढवते.",
                "description_hi": "जिंक, आयरन, बोरॉन युक्त सूक्ष्म पोषक मिश्रण। पत्तियों का पीलापन दूर करता है।",
                "category_id": category_map["fertilizers"],
                "price": 550.0,
                "original_price": 650.0,
                "discount_percent": 15,
                "unit_en": "500ml Bottle",
                "unit_mr": "५०० मिली बाटली",
                "unit_hi": "५०० मिली बोतल",
                "stock_quantity": 60,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?w=600&auto=format&fit=crop&q=80",
                "badge": "Grade-II",
                "rating": 4.8,
                "reviews_count": 28,
                "is_featured": False
            },

            # Pesticides / Crop Protection
            {
                "slug": "syngenta-ampligo-insecticide",
                "name_en": "Syngenta Ampligo Broad Spectrum Insecticide",
                "name_mr": "सिंजेन्टा अँप्लिगो प्रभावी कीटकनाशक",
                "name_hi": "सिंजेंटा एम्प्लिगो कीटनाशक",
                "description_en": "Advanced dual active technology for immediate knockdown and long-lasting control of bollworms, armyworms, and stem borers.",
                "description_mr": "बोंडअळी, लष्करी अळी, आणि खोडकिडीवर त्वरित आणि प्रदीर्घ नियंत्रण मिळवणारे जागतिक दर्जाचे औषध.",
                "description_hi": "इल्लियों, तना छेदक और कीटों पर तुरंत असरदार दोहरा एक्शन कीटनाशक।",
                "category_id": category_map["pesticides"],
                "price": 980.0,
                "original_price": 1150.0,
                "discount_percent": 14,
                "unit_en": "200ml Bottle",
                "unit_mr": "२०० मिली बाटली",
                "unit_hi": "२०० मिली बोतल",
                "stock_quantity": 75,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=600&auto=format&fit=crop&q=80",
                "badge": "Top Rated",
                "rating": 5.0,
                "reviews_count": 41,
                "is_featured": True
            },
            {
                "slug": "bayer-nativo-fungicide",
                "name_en": "Bayer Nativo Systemic Fungicide",
                "name_mr": "बायर नॅटिव्हो आंतरप्रवाही बुरशीनाशक",
                "name_hi": "बायेर नेटिवो फफूंदनाशक",
                "description_en": "Systemic fungicide providing superior protection against blast, sheath blight, powdery mildew, and anthracnose.",
                "description_mr": "करपा, भुरी, तांबेरा आणि बुरशीजन्य रोगांवर अत्यंत परिणामकारक आंतरप्रवाही बुरशीनाशक.",
                "description_hi": "ब्लास्ट, शीथ ब्लाइट और पाउडरी मिल्ड्यू फफूंद जनित रोगों पर अचूक सुरक्षा।",
                "category_id": category_map["pesticides"],
                "price": 720.0,
                "original_price": 820.0,
                "discount_percent": 12,
                "unit_en": "100g Pack",
                "unit_mr": "१०० ग्रॅम पॅक",
                "unit_hi": "१०० ग्राम पैक",
                "stock_quantity": 90,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=600&auto=format&fit=crop&q=80",
                "badge": "Bayer Original",
                "rating": 4.9,
                "reviews_count": 37,
                "is_featured": False
            },

            # Tools & Equipment
            {
                "slug": "balwan-16l-battery-sprayer-pump",
                "name_en": "Balwan 16L 12V Battery Knapsack Sprayer Pump",
                "name_mr": "बलवान १६ लिटर १२V बॅटरी स्प्रे पंप (फवारणी यंत्र)",
                "name_hi": "बलवान १६ लीटर १२V बैटरी स्प्रे पंप",
                "description_en": "Double motor 12V 12Ah heavy duty rechargeable battery sprayer. Covers 25-30 tanks per charge with 4 brass nozzles and telescopic lance.",
                "description_mr": "१२ व्होल्ट १२ एम्पिअर डबल मोटर बॅटरी पंप. एका चार्जिंगमध्ये २५-३० पंप फवारणी, ब्रास नोझल्स आणि स्टेनलेस स्टील रॉड.",
                "description_hi": "डबल मोटर शक्तिशाली बैटरी स्प्रे पंप। एक बार चार्ज करने पर २५-३० टंकी छिड़काव।",
                "category_id": category_map["equipment"],
                "price": 2899.0,
                "original_price": 3800.0,
                "discount_percent": 24,
                "unit_en": "1 Full Set",
                "unit_mr": "१ संपूर्ण संच",
                "unit_hi": "१ पूरा सेट",
                "stock_quantity": 30,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600&auto=format&fit=crop&q=80",
                "badge": "Best Seller",
                "rating": 4.9,
                "reviews_count": 89,
                "is_featured": True
            },
            {
                "slug": "rotary-manual-weed-remover",
                "name_en": "Heavy Duty Manual Wheel Weeder / Khurpi",
                "name_mr": "सायकल कोळपे / खुरपणी यंत्र (Heavy Duty)",
                "name_hi": "मैनुअल व्हील वीडर / साइकिल खरपतवार नाशक",
                "description_en": "Ergonomic wheeled hand-weeder for effortless weed removal in rows of cotton, vegetables, soybean and onion without bending.",
                "description_mr": "कापूस, कांदा, सोयाबीन व भाजीपाल्यामधील तण सहज काढण्यासाठी उपयुक्त सायकल कोळपे. पाठीचा त्रास वाचवणारे यंत्र.",
                "description_hi": "सब्जियों और फसलों के बीच से आसानी से खरपतवार निकालने वाला मजबूत व्हील वीडर।",
                "category_id": category_map["equipment"],
                "price": 1250.0,
                "original_price": 1600.0,
                "discount_percent": 22,
                "unit_en": "1 Piece",
                "unit_mr": "१ नग",
                "unit_hi": "१ नग",
                "stock_quantity": 45,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1592417817098-8f3d6ef22569?w=600&auto=format&fit=crop&q=80",
                "badge": "Farmer Choice",
                "rating": 4.6,
                "reviews_count": 24,
                "is_featured": False
            },
            {
                "slug": "digital-soil-ph-moisture-meter",
                "name_en": "4-in-1 Digital Soil pH & Moisture Tester",
                "name_mr": "४-इन-१ डिजिटल जमीन pH व आर्द्रता तपासणी यंत्र",
                "name_hi": "४-इन-१ डिजिटल मृदा pH एवं नमी टेस्टर",
                "description_en": "Measures soil pH, moisture, temperature, and sunlight intensity instantly. Helps in scientific fertilization and irrigation planning.",
                "description_mr": "जमिनीचा सामू (pH), ओलावा, तापमान आणि सूर्यप्रकाश मोजणारे आधुनिक डिजिटल मीटर. अचूक खत व्यवस्थापनासाठी उपयुक्त.",
                "description_hi": "मिट्टी की उर्वरता, नमी और pH स्तर मापने का आसान डिजिटल यंत्र।",
                "category_id": category_map["equipment"],
                "price": 999.0,
                "original_price": 1499.0,
                "discount_percent": 33,
                "unit_en": "1 Piece",
                "unit_mr": "१ नग",
                "unit_hi": "१ नग",
                "stock_quantity": 50,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600&auto=format&fit=crop&q=80",
                "badge": "Smart Tool",
                "rating": 4.7,
                "reviews_count": 19,
                "is_featured": False
            },

            # Irrigation
            {
                "slug": "jain-drip-lateral-pipe-16mm",
                "name_en": "Jain Drip Inline Lateral Pipe 16mm (400m Roll)",
                "name_mr": "जैन ठिबक सिंचन इनलाईन लॅटरल १६ मिमी (४०० मी. बंडल)",
                "name_hi": "जैन ड्रिप इनलाइन लेटरल पाइप १६ मिमी (४०० मी. बंडल)",
                "description_en": "ISI marked high-density UV stabilized drip tubing with 40cm emitter spacing (4 LPH). 10-year field lifespan for sugarcane, cotton, and orchards.",
                "description_mr": "आयएसआय प्रमाणित, सूर्यप्रकाश रोधक १६ मिमी ठिबक नळी. ऊस, कापूस, डाळिंब, पेरू व भाजीपाल्यासाठी दीर्घकाळ टिकणारे पाणी बचत साधन.",
                "description_hi": "आईएसआई मार्क १६ मिमी ड्रिप लेटरल पाइप। पानी की ७०% बचत और फसलों की शानदार उपज।",
                "category_id": category_map["irrigation"],
                "price": 2450.0,
                "original_price": 2900.0,
                "discount_percent": 15,
                "unit_en": "400m Roll",
                "unit_mr": "४०० मीटर बंडल",
                "unit_hi": "४०० मीटर बंडल",
                "stock_quantity": 25,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=600&auto=format&fit=crop&q=80",
                "badge": "ISI Certified",
                "rating": 4.9,
                "reviews_count": 52,
                "is_featured": True
            },
            {
                "slug": "brass-rain-gun-sprinkler-1-5-inch",
                "name_en": "1.5 Inch Brass Rain Gun Impact Sprinkler with Stand",
                "name_mr": "१.५ इंच ब्रास रेन गन तुषार सिंचन स्टँडसह",
                "name_hi": "१.५ इंच पीतल रेन गन स्प्रिंकलर स्टैंड सहित",
                "description_en": "Heavy brass rain gun with 30-40 meter circular spray radius. Perfect for wheat, gram, sugarcane, groundnut, and fodder lawns.",
                "description_mr": "३० ते ४० मीटर गोलाकार फवारणी क्षमतेची हेवी ब्रास रेन गन. गहू, हरभरा, चारा पिके व भाजीपाल्यासाठी एकसमान पाणी देणारे साधन.",
                "description_hi": "३० से ४० मीटर दूरी तक बारिश जैसा छिड़काव करने वाला रेन गन स्प्रिंकलर।",
                "category_id": category_map["irrigation"],
                "price": 3199.0,
                "original_price": 4200.0,
                "discount_percent": 24,
                "unit_en": "1 Gun + Tripod",
                "unit_mr": "१ गन + ट्रायपॉड",
                "unit_hi": "१ गन + ट्राइपॉड",
                "stock_quantity": 20,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1515150144380-bca9f1650ed9?w=600&auto=format&fit=crop&q=80",
                "badge": "Water Saver",
                "rating": 4.8,
                "reviews_count": 31,
                "is_featured": False
            },

            # Organic Farming
            {
                "slug": "pure-neem-oil-10000-ppm",
                "name_en": "Pure Cold Pressed Neem Oil 10,000 PPM Bio-Pesticide",
                "name_mr": "शुद्ध कडुनिंब तेल १०००० PPM सेंद्रिय कीटकनाशक",
                "name_hi": "शुद्ध नीम का तेल १०,००० पीपीएम जैविक कीटनाशक",
                "description_en": "100% natural, eco-friendly azadirachtin neem oil. Effectively controls sucking pests, whiteflies, thrips, aphids and fungal spores organically.",
                "description_mr": "१००% नैसर्गिक कडुनिंब तेल. मावा, तुडतुडे, पांढरी माशी आणि रोगांवर उत्कृष्ट सेंद्रिय उपाय. पिकांवर कसलाही विषारी परिणाम नाही.",
                "description_hi": "प्राकृतिक नीम अर्क जो माहू, सफेद मक्खी और थ्रिप्स को प्राकृतिक रूप से नियंत्रित करता है।",
                "category_id": category_map["organic"],
                "price": 450.0,
                "original_price": 550.0,
                "discount_percent": 18,
                "unit_en": "1 Litre Bottle",
                "unit_mr": "१ लिटर बाटली",
                "unit_hi": "१ लीटर बोतल",
                "stock_quantity": 90,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?w=600&auto=format&fit=crop&q=80",
                "badge": "100% Organic",
                "rating": 4.9,
                "reviews_count": 68,
                "is_featured": True
            },
            {
                "slug": "premium-vermicompost-fertilizer",
                "name_en": "Organic Earthworm Vermicompost (Gandul Khat)",
                "name_mr": "सेंद्रिय गांडूळ खत (Vermicompost - १००% शुद्ध)",
                "name_hi": "जैविक केंचुआ खाद (वर्मीकम्पोस्ट)",
                "description_en": "Nutrient-rich organic vermicompost packed with beneficial microbes, humus, and carbon to rejuvenate soil fertility and water holding capacity.",
                "description_mr": "सेंद्रिय गांडूळ खत. जमिनीचा पोत सुधारते, सेंद्रिय कर्ब वाढवते आणि पिकांची रोगप्रतिकारक शक्ती मजबूत करते.",
                "description_hi": "पोषक तत्वों से भरपूर शुद्ध जैविक केंचुआ खाद। मिट्टी की उर्वरता और जल धारण क्षमता बढ़ाता है।",
                "category_id": category_map["organic"],
                "price": 380.0,
                "original_price": 480.0,
                "discount_percent": 20,
                "unit_en": "25 Kg Bag",
                "unit_mr": "२५ किलो बॅग",
                "unit_hi": "२५ किग्रा थैला",
                "stock_quantity": 100,
                "in_stock": True,
                "image_url": "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=600&auto=format&fit=crop&q=80",
                "badge": "Eco Friendly",
                "rating": 4.8,
                "reviews_count": 55,
                "is_featured": False
            }
        ]

        for p in products_data:
            prod_obj = Product(**p)
            db.add(prod_obj)
        db.commit()
        print(f"[*] {len(products_data)} realistic agricultural products seeded.")
