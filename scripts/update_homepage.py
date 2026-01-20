import os
import sys
import xmlrpc.client

# Add src to path
sys.path.append(os.getcwd())

def run():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    username = os.getenv("ODOO_USER", "admin")
    password = os.getenv("ODOO_PASSWORD", "admin")
    db = "bearings"

    print(f"Connecting to {url} (db: {db})...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # New Homepage Content (Simple, Clean, Professional)
        # Using Odoo Snippet Structure (s_cover, s_text_image, s_call_to_action)
        new_arch = """<t name="Home" t-name="website.homepage">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'homepage'"/>
        <div id="wrap" class="oe_structure oe_empty">
            
            <!-- HERO SECTION -->
            <section class="s_cover parallax s_parallax_is_fixed bg-black-50 pt96 pb96" data-scroll-background-ratio="1">
                <span class="s_parallax_bg oe_img_bg" style="background-image: url('/web/image/website.s_cover_default_image'); background-position: 50% 0;"></span>
                <div class="container s_cover_content container-fluid">
                    <div class="row">
                        <div class="col-lg-12 text-center pt96 pb96">
                            <h1 class="display-3" style="font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Premium Industrial Bearings</h1>
                            <p class="lead" style="font-size: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">High-Performance Components for Automotive &amp; Heavy Industry.</p>
                            <div class="pt32">
                                <a href="/shop" class="btn btn-primary btn-lg rounded-circle">Browse Catalog</a>
                                <a href="/about-us" class="btn btn-outline-light btn-lg rounded-circle">About Us</a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- FEATURES SECTION -->
            <section class="s_features pt64 pb64 bg-100">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-4 text-center">
                            <i class="fa fa-cogs fa-5x text-primary mb-3"></i>
                            <h3>Wide Selection</h3>
                            <p>Over 2,000 SKUs of Spherical, Tapered, and Precision Bearings.</p>
                        </div>
                        <div class="col-lg-4 text-center">
                            <i class="fa fa-truck fa-5x text-primary mb-3"></i>
                            <h3>Fast Shipping</h3>
                            <p>Global logistics partners ensuring rapid delivery to your facility.</p>
                        </div>
                        <div class="col-lg-4 text-center">
                            <i class="fa fa-check-circle fa-5x text-primary mb-3"></i>
                            <h3>Quality Guaranteed</h3>
                            <p>Authorized distributor for top brands like SKF, Timken, and FAG.</p>
                        </div>
                    </div>
                </div>
            </section>

             <!-- CALL TO ACTION -->
            <section class="s_call_to_action pt64 pb64 bg-primary text-white">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-9">
                            <h3>Ready to optimize your machinery?</h3>
                            <p>Contact our engineering team for custom solutions.</p>
                        </div>
                        <div class="col-lg-3 text-right">
                            <a href="/contactus" class="btn btn-light btn-lg">Contact Sales</a>
                        </div>
                    </div>
                </div>
            </section>

        </div>
    </t>
</t>"""
        
        # Write to view ID 1059 (found in previous step)
        # Use a search just to be safe
        views = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[('key', '=', 'website.homepage')]])
        if views:
            print(f"Updating Homepage View ID: {views[0]}...")
            models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[views[0]], {'arch': new_arch}])
            print("✅ Homepage Updated with new Professional Design.")
        else:
            print("❌ View not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
