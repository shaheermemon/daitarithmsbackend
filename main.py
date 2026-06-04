from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, text
from pydantic import BaseModel
from typing import Optional

from database import SessionLocal, engine, Base
import models

# Create tables (only first run)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Website Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------
# DATABASE DEPENDENCY
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# PYDANTIC SCHEMAS
# ---------------------------
class FeatureCreate(BaseModel):
    title: str
    description: str


class FeatureUpdate(BaseModel):
    title: str
    description: str


# ---------------------------
# ROOT
# ---------------------------
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# ---------------------------
# GET ALL FEATURES
# ---------------------------
@app.get("/features")
def get_features(db: Session = Depends(get_db)):
    return db.query(models.Feature).all()


# ---------------------------
# ADD FEATURE
# ---------------------------
@app.post("/features")
def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    new_feature = models.Feature(
        title=feature.title,
        description=feature.description
    )
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return new_feature


# ---------------------------
# UPDATE FEATURE
# ---------------------------
@app.put("/features/{feature_id}")
def update_feature(feature_id: int, feature: FeatureUpdate, db: Session = Depends(get_db)):
    db_feature = db.query(models.Feature).filter(models.Feature.id == feature_id).first()

    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    db_feature.title = feature.title
    db_feature.description = feature.description

    db.commit()
    db.refresh(db_feature)
    return db_feature


# ---------------------------
# DELETE FEATURE
# ---------------------------
@app.delete("/features/{feature_id}")
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    db_feature = db.query(models.Feature).filter(models.Feature.id == feature_id).first()

    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    db.delete(db_feature)
    db.commit()

    return {"message": "Feature deleted successfully"}




class MenuCreate(BaseModel):
    title: str
    link: str
    position: int

@app.get("/menus")
def get_menus(db: Session = Depends(get_db)):
    return db.query(models.Menu).order_by(models.Menu.position).all()

@app.post("/menus")
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):

    new_menu = models.Menu(
        title=menu.title,
        link=menu.link,
        position=menu.position
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return new_menu

@app.delete("/menus/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):

    menu = db.query(models.Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    db.delete(menu)
    db.commit()

    return {"message": "Menu deleted successfully"}




# =========================
# HERO SECTION
# =========================

@app.get("/hero")
def get_hero(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM hero_section LIMIT 1")).mappings().first()


# =========================
# STATS
# =========================

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM stats"))
    return result.mappings().all()


# =========================
# UPDATE HERO
# =========================

class HeroUpdate(BaseModel):
    title: str
    subtitle: str
    description: str
    button1_text: str
    button1_link: str
    button2_text: str
    button2_link: str
    email: str


@app.put("/hero/{hero_id}")
def update_hero(hero_id: int, hero: HeroUpdate, db: Session = Depends(get_db)):

    db.execute(
        text("""
            UPDATE hero_section
            SET
                title = :title,
                subtitle = :subtitle,
                description = :description,
                button1_text = :button1_text,
                button1_link = :button1_link,
                button2_text = :button2_text,
                button2_link = :button2_link,
                email = :email
            WHERE id = :id
        """),
        {
            "id": hero_id,
            "title": hero.title,
            "subtitle": hero.subtitle,
            "description": hero.description,
            "button1_text": hero.button1_text,
            "button1_link": hero.button1_link,
            "button2_text": hero.button2_text,
            "button2_link": hero.button2_link,
            "email": hero.email
        }
    )

    db.commit()

    return {"message": "Hero updated successfully"}



# =========================
# ADD STAT
# =========================

class StatCreate(BaseModel):
    number: str
    label: str


@app.post("/stats")
def create_stat(stat: StatCreate, db: Session = Depends(get_db)):

    db.execute(
        text("""
            INSERT INTO stats (number, label)
            VALUES (:number, :label)
        """),
        {
            "number": stat.number,
            "label": stat.label
        }
    )

    db.commit()

    return {"message": "Stat added successfully"}


# =========================
# DELETE STAT
# =========================

@app.delete("/stats/{stat_id}")
def delete_stat(stat_id: int, db: Session = Depends(get_db)):

    db.execute(
        text("DELETE FROM stats WHERE id = :id"),
        {"id": stat_id}
    )

    db.commit()

    return {"message": "Stat deleted successfully"}


# =====================================
# FOUNDERS
# =====================================

class FounderCreate(BaseModel):
    name: str
    role: str
    degree: str
    university: str
    expertise: str
    achievements: str
    image: Optional[str] = None


@app.get("/founders")
def get_founders(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM founders ORDER BY id")
    )

    return result.mappings().all()


@app.post("/founders")
def create_founder(
    founder: FounderCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO founders
            (
                name,
                role,
                degree,
                university,
                expertise,
                achievements,
                image
            )

            VALUES
            (
                :name,
                :role,
                :degree,
                :university,
                :expertise,
                :achievements,
                :image
            )
        """),
        founder.dict()
    )

    db.commit()

    return {"message": "Founder added successfully"}



# =====================================
# TEAM
# =====================================

class TeamCreate(BaseModel):
    name: str
    role: str
    description: str
    skills: str
    image: Optional[str] = None


@app.get("/team")
def get_team(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM team ORDER BY id")
    )

    return result.mappings().all()


@app.post("/team")
def create_team_member(
    member: TeamCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO team
            (
                name,
                role,
                description,
                skills,
                image
            )

            VALUES
            (
                :name,
                :role,
                :description,
                :skills,
                :image
            )
        """),
        member.dict()
    )

    db.commit()

    return {"message": "Team member added successfully"}


# =====================================
# VISION
# =====================================

@app.get("/vision")
def get_vision(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM vision LIMIT 1")
    )

    return result.mappings().first()


# =====================================
# DELETE FOUNDER
# =====================================

@app.delete("/founders/{founder_id}")
def delete_founder(founder_id: int, db: Session = Depends(get_db)):

    db.execute(
        text("DELETE FROM founders WHERE id = :id"),
        {"id": founder_id}
    )

    db.commit()

    return {"message": "Founder deleted successfully"}


# =====================================
# DELETE TEAM MEMBER
# =====================================

@app.delete("/team/{member_id}")
def delete_team_member(member_id: int, db: Session = Depends(get_db)):

    db.execute(
        text("DELETE FROM team WHERE id = :id"),
        {"id": member_id}
    )

    db.commit()

    return {"message": "Team member deleted successfully"}


# =====================================
# ABOUT SECTION
# =====================================

class AboutUpdate(BaseModel):
    title: str
    description: str
    mission: str
    vision: str


@app.get("/about")
def get_about(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM about LIMIT 1")
    )

    return result.mappings().first()


@app.put("/about")
def update_about(
    about: AboutUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE about
            SET
                title = :title,
                description = :description,
                mission = :mission,
                vision = :vision
            WHERE id = 1
        """),
        {
            "title": about.title,
            "description": about.description,
            "mission": about.mission,
            "vision": about.vision,
        }
    )

    db.commit()

    return {"message": "About updated successfully"}


# =====================================
# UPDATE VISION
# =====================================

class VisionUpdate(BaseModel):
    content: str


@app.put("/vision")
def update_vision(
    vision: VisionUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE vision
            SET content = :content
            WHERE id = 1
        """),
        {
            "content": vision.content
        }
    )

    db.commit()

    return {"message": "Vision updated successfully"}



# =====================================
# SERVICES PAGE
# =====================================

class ServiceCreate(BaseModel):
    title: str
    description: str
    icon: str
    points: str


@app.get("/services")
def get_services(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM services ORDER BY id")
    )

    return result.mappings().all()


@app.post("/services")
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO services
            (
                title,
                description,
                icon,
                points
            )

            VALUES
            (
                :title,
                :description,
                :icon,
                :points
            )
        """),
        service.dict()
    )

    db.commit()

    return {"message": "Service added successfully"}


@app.delete("/services/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):

    db.execute(
        text("DELETE FROM services WHERE id = :id"),
        {"id": service_id}
    )

    db.commit()

    return {"message": "Deleted successfully"}


# =====================================
# PROCESS SECTION
# =====================================

class ProcessCreate(BaseModel):
    number: str
    title: str
    description: str


@app.get("/process")
def get_process(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM process_steps ORDER BY id")
    )

    return result.mappings().all()


@app.post("/process")
def create_process(
    process: ProcessCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO process_steps
            (
                number,
                title,
                description
            )

            VALUES
            (
                :number,
                :title,
                :description
            )
        """),
        process.dict()
    )

    db.commit()

    return {"message": "Process added successfully"}


@app.delete("/process/{process_id}")
def delete_process(
    process_id: int,
    db: Session = Depends(get_db)
):

    db.execute(
        text("DELETE FROM process_steps WHERE id = :id"),
        {"id": process_id}
    )

    db.commit()

    return {"message": "Deleted successfully"}


# =====================================
# SERVICE PAGE HERO
# =====================================

@app.get("/service-page")
def get_service_page(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM service_page LIMIT 1")
    )

    return result.mappings().first()


class ServicePageUpdate(BaseModel):
    hero_title: str
    hero_description: str


@app.put("/service-page")
def update_service_page(
    data: ServicePageUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE service_page
            SET
                hero_title = :hero_title,
                hero_description = :hero_description
            WHERE id = 1
        """),
        data.dict()
    )

    db.commit()

    return {"message": "Updated successfully"}



# =====================================
# INDUSTRIES
# =====================================

class IndustryCreate(BaseModel):
    title: str
    description: str
    solutions: str
    projects: str
    clients: str
    image: Optional[str] = None


@app.get("/industries")
def get_industries(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM industries ORDER BY id")
    )

    return result.mappings().all()


@app.post("/industries")
def create_industry(
    industry: IndustryCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO industries
            (
                title,
                description,
                solutions,
                projects,
                clients,
                image
            )

            VALUES
            (
                :title,
                :description,
                :solutions,
                :projects,
                :clients,
                :image
            )
        """),
        industry.dict()
    )

    db.commit()

    return {"message": "Industry added successfully"}


@app.delete("/industries/{industry_id}")
def delete_industry(industry_id: int, db: Session = Depends(get_db)):

    db.execute(
        text("DELETE FROM industries WHERE id = :id"),
        {"id": industry_id}
    )

    db.commit()

    return {"message": "Industry deleted successfully"}

# =====================================
# INDUSTRIES HEADER
# =====================================

class IndustriesHeaderUpdate(BaseModel):
    title: str
    subtitle: str


@app.get("/industries-header")
def get_industries_header(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM industries_header LIMIT 1")
    )

    return result.mappings().first()


@app.put("/industries-header")
def update_industries_header(
    data: IndustriesHeaderUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE industries_header
            SET
                title = :title,
                subtitle = :subtitle
            WHERE id = 1
        """),
        data.dict()
    )

    db.commit()

    return {"message": "Industries header updated"}



# =====================================
# THEME SETTINGS
# =====================================

class ThemeUpdate(BaseModel):

    primary_color: str
    secondary_color: str

    background_color: str
    card_color: str

    text_color: str
    text_secondary: str

    navbar_color: str
    footer_color: str

    border_color: str

    button_color: str
    button_text_color: str

    hero_gradient_from: str
    hero_gradient_to: str


@app.get("/theme")
def get_theme(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM theme_settings LIMIT 1")
    )

    return result.mappings().first()


@app.put("/theme/{theme_id}")
def update_theme(
    theme_id: int,
    theme: ThemeUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE theme_settings
            SET

            primary_color = :primary_color,
            secondary_color = :secondary_color,

            background_color = :background_color,
            card_color = :card_color,

            text_color = :text_color,
            text_secondary = :text_secondary,

            navbar_color = :navbar_color,
            footer_color = :footer_color,

            border_color = :border_color,

            button_color = :button_color,
            button_text_color = :button_text_color,

            hero_gradient_from = :hero_gradient_from,
            hero_gradient_to = :hero_gradient_to

            WHERE id = :id
        """),

        {
            "id": theme_id,
            **theme.dict()
        }
    )

    db.commit()

    return {"message": "Theme updated successfully"}



# =====================================
# CONTACT PAGE
# =====================================

class ContactPageUpdate(BaseModel):
    title: str
    subtitle: str
    description: str
    email: str
    whatsapp: str
    info_title: str
    choose_title: str
    form_title: str
    feature1: str
    feature2: str
    feature3: str
    feature4: str


class ContactMessageCreate(BaseModel):
    name: str
    email: str
    message: str


# GET CONTACT PAGE
@app.get("/contact-page")
def get_contact_page(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM contact_page LIMIT 1")
    )

    return result.mappings().first()


# UPDATE CONTACT PAGE
@app.put("/contact-page")
def update_contact_page(
    data: ContactPageUpdate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE contact_page
            SET
                title = :title,
                subtitle = :subtitle,
                description = :description,
                email = :email,
                whatsapp = :whatsapp,
                info_title = :info_title,
                choose_title = :choose_title,
                form_title = :form_title,
                feature1 = :feature1,
                feature2 = :feature2,
                feature3 = :feature3,
                feature4 = :feature4
            WHERE id = 1
        """),
        data.dict()
    )

    db.commit()

    return {"message": "Updated Successfully"}


# SAVE CONTACT MESSAGE
@app.post("/contact-message")
def add_contact_message(
    data: ContactMessageCreate,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            INSERT INTO contact_messages
            (
                name,
                email,
                message
            )

            VALUES
            (
                :name,
                :email,
                :message
            )
        """),
        data.dict()
    )

    db.commit()

    return {"message": "Message Saved Successfully"}


# GET ALL CONTACT MESSAGES
@app.get("/contact-messages")
def get_contact_messages(db: Session = Depends(get_db)):

    result = db.execute(
        text("""
            SELECT * FROM contact_messages
            ORDER BY id DESC
        """)
    )

    return result.mappings().all()    



# =====================================
# SITE SETTINGS
# =====================================

class SiteSettings(BaseModel):
    website_name: str
    logo: str


@app.get("/site-settings")
def get_site_settings(db: Session = Depends(get_db)):

    result = db.execute(
        text("SELECT * FROM site_settings LIMIT 1")
    )

    return result.mappings().first()


@app.put("/site-settings")
def update_site_settings(
    data: SiteSettings,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE site_settings
            SET
                website_name = :website_name,
                logo = :logo
            WHERE id = 1
        """),
        data.dict()
    )

    db.commit()

    return {"message": "Site settings updated"}



# =====================================
# COMPLETE WEBSITE DATA API
# =====================================

@app.get("/website-data")
def get_website_data(db: Session = Depends(get_db)):

    # HERO
    hero = db.execute(
        text("SELECT * FROM hero_section LIMIT 1")
    ).mappings().first()

    # MENUS
    menus = db.execute(
        text("SELECT * FROM menus ORDER BY position")
    ).mappings().all()

    # FEATURES
    features = db.execute(
        text("SELECT * FROM features ORDER BY id")
    ).mappings().all()

    # STATS
    stats = db.execute(
        text("SELECT * FROM stats ORDER BY id")
    ).mappings().all()

    # ABOUT
    about = db.execute(
        text("SELECT * FROM about LIMIT 1")
    ).mappings().first()

    # FOUNDERS
    founders = db.execute(
        text("SELECT * FROM founders ORDER BY id")
    ).mappings().all()

    # TEAM
    team = db.execute(
        text("SELECT * FROM team ORDER BY id")
    ).mappings().all()

    # VISION
    vision = db.execute(
        text("SELECT * FROM vision LIMIT 1")
    ).mappings().first()

    # SERVICES
    services = db.execute(
        text("SELECT * FROM services ORDER BY id")
    ).mappings().all()

    # PROCESS
    process = db.execute(
        text("SELECT * FROM process_steps ORDER BY id")
    ).mappings().all()

    # SERVICE PAGE
    service_page = db.execute(
        text("SELECT * FROM service_page LIMIT 1")
    ).mappings().first()

    # INDUSTRIES
    industries = db.execute(
        text("SELECT * FROM industries ORDER BY id")
    ).mappings().all()

    # INDUSTRIES HEADER
    industries_header = db.execute(
        text("SELECT * FROM industries_header LIMIT 1")
    ).mappings().first()

    # CONTACT PAGE
    contact_page = db.execute(
        text("SELECT * FROM contact_page LIMIT 1")
    ).mappings().first()

    # THEME
    theme = db.execute(
        text("SELECT * FROM theme_settings LIMIT 1")
    ).mappings().first()

    return {
        "hero": hero,
        "menus": menus,
        "features": features,
        "stats": stats,
        "about": about,
        "founders": founders,
        "team": team,
        "vision": vision,
        "services": services,
        "process": process,
        "service_page": service_page,
        "industries": industries,
        "industries_header": industries_header,
        "contact_page": contact_page,
        "theme": theme
    }