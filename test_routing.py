import extra_streamlit_components as stx
import streamlit as st
from test_streamlit import a

@st.cache_resource
def init_router():
    return stx.Router({"/home": home, "/landing": landing, '/shop_base': shop_base})


def home():
    st.write("This is a home page")

def landing():
    return st.write("This is the landing page")

def shop_base():
    a(shop_id=st.session_state['shop_id'])

st.set_page_config(page_title=f"Test",
                page_icon=":bar_chart:", layout="wide")

if 'shop_id' not in st.session_state:
    st.session_state['shop_id'] = ''
router = init_router()
router.show_route_view()

c1, c2, c3 = st.columns(3)

with c1:
    st.header("Current route")
    current_route = router.get_url_route()
    st.write(f"{current_route}")
with c2:
    st.header("Set route")
    new_route = st.text_input("route")
    st.caption("You can try to set route to '/shop_base' and shop_id = 70628044 or 302237436.")
    st.header("Set shop_id")
    shopid_input = st.text_input(
        'Input your shop id:', st.session_state['shop_id'])
    if st.button("Route now!"):
        st.session_state['shop_id'] = shopid_input
        router.route(new_route)
with c3:
    st.header("Session state")
    st.write(st.session_state)
