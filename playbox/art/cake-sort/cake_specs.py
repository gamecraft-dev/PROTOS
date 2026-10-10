# Cake Sort slices: what each cake is made of. Colours and layers follow the game's CAKES table
# (playbox/src/games/cake-sort.html), a touch deeper where 3D lighting would wash them out.
#
# sponge   the cake's crumb: base, light (mottling), pore, crust, crust_dark (the very bottom), shade
#          (the sponge in a filling's shadow)
# bands    the fillings seen where the slice is cut, bottom to top: (z from, z to, colour, darker, kind);
#          kind 'cream' is puffy and soft, 'jam' is smooth and glossy (curd, jam, ganache, caramel)
# coat     style 'full': a coat over the top and all the way down the outside (a frosted cake);
#          'naked': a glaze over the top that drips down bare sides; 'cap': a thick cream top over
#          bare sides. kind 'glaze' is glossy, 'frosting' matte buttercream or cream cheese.
#          band: how far the coat reaches down a cut face; drips: 'glaze' (as the strawberry) or None
# pipe     the colour of a piped rosette under the topping, or None
# pattern  what decorates the top: swirl, drizzle, dust, sprinkles, crumbs, or None
# topping  the piece on top that tells the cakes apart at a glance
# ink      the outline colour (the slice shader's outline and the renders' ink)

def stack(layers, z_top=0.62):
    """Fillings from the game's layer shares (bottom to top, the top coat left out), fitted below z_top."""
    total = sum(l[0] for l in layers); z = 0.0; out = []
    for share, kind, col, shade in layers:
        z1 = z + share / total * z_top
        if kind != 'sponge': out.append((round(z, 4), round(z1, 4), col, shade, kind))
        z = z1
    return out

SP = ('sponge', None, None)

SPECS = {
    'strawberry': dict(
        title='Strawberry', ink='#4A1626',
        sponge=dict(base='#F0C47A', light='#FADFA6', pore='#DCA24F', crust='#CF8442', crust_dark='#B9692F', shade='#D9A160'),
        bands=[(0.2, 0.317, '#FFF6E8', '#F4E2C8', 'cream'), (0.43, 0.542, '#FFF6E8', '#F4E2C8', 'cream')],
        coat=dict(style='full', kind='glaze', base='#F7819F', ramp=[(0.0, '#E2617F'), (0.55, '#EF7395'), (0.72, '#F48AA6')],
                  edge='#D8557A', rough=0.2, coat=0.55, coat_rough=0.09, sss=0.2, sss_radius=(1, .35, .4), band=0.095, drips='glaze'),
        pipe='#FBF0DE', pattern=None, topping='strawberry', outer_drips=None),

    'chocolate': dict(
        title='Chocolate', ink='#24100A',
        sponge=dict(base='#6E3A24', light='#87502F', pore='#4E2616', crust='#4A2414', crust_dark='#3A1C10', shade='#55291A'),
        bands=stack([(.32,) + SP, (.1, 'jam', '#2F150A', '#24100A'), (.32,) + SP]),
        # milk-chocolate frosting down the sides, dark ganache over the top and running down in drips
        coat=dict(style='full', kind='glaze', base='#7A4628', ramp=[(0.0, '#6A3A20'), (0.5, '#80492A'), (0.66, '#8A5232'), (0.69, '#43200E'), (0.72, '#4E2612')],
                  edge='#5A2E18', rough=0.24, coat=0.5, coat_rough=0.1, sss=0.04, sss_radius=(1, .5, .3), band=0.095, drips='glaze'),
        pipe=None, pattern=dict(kind='swirl', colour='#5E2F1A'), topping='choc',
        outer_drips=dict(colour='#3E1C0C', light='#4E2612')),

    'lemon': dict(
        title='Lemon', ink='#4A3008',
        sponge=dict(base='#F8E39A', light='#FFF3C4', pore='#E8C86A', crust='#DDA24E', crust_dark='#BE8236', shade='#E9CB7A'),
        bands=stack([(.3,) + SP, (.08, 'jam', '#FFCB12', '#F0B400'), (.08, 'cream', '#FFFBEA', '#F2EBCF'), (.3,) + SP]),
        coat=dict(style='naked', kind='glaze', base='#FFDF45', ramp=[(0.5, '#F2C21E'), (0.62, '#FFD535'), (0.72, '#FFE35A')],
                  edge='#E3AE10', rough=0.14, coat=0.6, coat_rough=0.06, sss=0.3, sss_radius=(1, .8, .2), band=0.075, drips='glaze'),
        pipe='#FFFBEA', pattern=None, topping='lemon', outer_drips=None),

    'matcha': dict(
        title='Matcha', ink='#1F3A16',
        sponge=dict(base='#B2D383', light='#CDE6A8', pore='#93BB62', crust='#7FA24E', crust_dark='#6A8A40', shade='#9CC06C'),
        bands=stack([(.3,) + SP, (.1, 'cream', '#F8F4E4', '#E9E2CB'), (.3,) + SP]),
        coat=dict(style='full', kind='frosting', base='#8DC35F', ramp=[(0.0, '#71A846'), (0.55, '#82B954'), (0.72, '#92C664')],
                  rough=0.62, coat=0.04, sss=0.08, sss_radius=(.6, 1, .4), band=0.12, drips=None),
        pipe='#F8F4E4', pattern=dict(kind='dust', colour='#557F33'), topping='leaf', outer_drips=None),

    'blueberry': dict(
        title='Blueberry', ink='#2A1A4A',
        sponge=dict(base='#F1DDB6', light='#FAEDD5', pore='#DDBF8C', crust='#D09A58', crust_dark='#B07A3C', shade='#DDB97F'),
        bands=stack([(.3,) + SP, (.08, 'jam', '#5B3FA8', '#46308A'), (.08, 'cream', '#ECE3FF', '#D9CCF2'), (.3,) + SP]),
        coat=dict(style='full', kind='frosting', base='#A887EC', ramp=[(0.0, '#8C6AD6'), (0.55, '#9B79E2'), (0.72, '#AD8DEE')],
                  rough=0.55, coat=0.05, sss=0.08, sss_radius=(.8, .6, 1), band=0.12, drips=None),
        pipe='#ECE3FF', pattern=None, topping='berries', outer_drips=None),

    'birthday': dict(
        title='Birthday', ink='#18304A',
        sponge=dict(base='#F7E6BC', light='#FFF5DE', pore='#E6CC92', crust='#D9A35C', crust_dark='#B98340', shade='#E5C98C'),
        bands=stack([(.3,) + SP, (.1, 'cream', '#FFFDF8', '#EFEAE0'), (.3,) + SP]),
        coat=dict(style='full', kind='frosting', base='#7BCFF5', ramp=[(0.0, '#58B4E4'), (0.55, '#67C1EB'), (0.72, '#82D2F6')],
                  rough=0.55, coat=0.05, sss=0.08, sss_radius=(.5, .8, 1), band=0.12, drips=None),
        pipe='#FFFDF9', pattern=dict(kind='sprinkles', colours=['#FF5A8A', '#FFD23F', '#5AD17F', '#FFFFFF', '#B57BFF', '#FF9A3D']),
        topping='candle', outer_drips=None),

    'mango': dict(
        title='Mango', ink='#4A2408',
        sponge=dict(base='#F9D690', light='#FFEAC0', pore='#E8BC66', crust='#DC9A48', crust_dark='#BC7A30', shade='#E9C07A'),
        bands=stack([(.3,) + SP, (.08, 'jam', '#FF9C1A', '#E8840A'), (.08, 'cream', '#FFF5E0', '#F1E4C6'), (.3,) + SP]),
        coat=dict(style='naked', kind='glaze', base='#FFA22C', ramp=[(0.5, '#EE8410'), (0.62, '#FF9A22'), (0.72, '#FFAD42')],
                  edge='#D96E04', rough=0.14, coat=0.6, coat_rough=0.06, sss=0.3, sss_radius=(1, .6, .2), band=0.075, drips='glaze'),
        pipe=None, pattern=None, topping='cubes', outer_drips=None),

    'cookies': dict(
        title='Cookies & Cream', ink='#1E1A19',
        sponge=dict(base='#3A322F', light='#4A413D', pore='#262120', crust='#2A2321', crust_dark='#1E1918', shade='#2E2826'),
        bands=stack([(.28,) + SP, (.12, 'cream', '#F6F2EB', '#E6E0D5'), (.28,) + SP], z_top=0.5),
        coat=dict(style='cap', kind='frosting', base='#F6F2EB', ramp=[(0.4, '#E8E2D7'), (0.6, '#F2EEE6'), (0.72, '#FAF8F3')],
                  rough=0.5, coat=0.05, sss=0.15, sss_radius=(1, .9, .8), band=0.215, drips=None),
        pipe=None, pattern=dict(kind='crumbs', colour='#2B2523', light='#4A4441'), topping='cookie', outer_drips=None),

    'redvelvet': dict(
        title='Red Velvet', ink='#3E0A14',
        sponge=dict(base='#A81529', light='#C42A3E', pore='#7E0E1D', crust='#7A0E1C', crust_dark='#5E0A15', shade='#8E1224'),
        bands=stack([(.3,) + SP, (.1, 'cream', '#FFF5EC', '#EFE2D4'), (.3,) + SP], z_top=0.5),
        coat=dict(style='cap', kind='frosting', base='#FFF5EC', ramp=[(0.4, '#F0E4D8'), (0.6, '#F9F0E7'), (0.72, '#FFFAF4')],
                  rough=0.5, coat=0.05, sss=0.15, sss_radius=(1, .85, .8), band=0.21, drips=None),
        pipe=None, pattern=dict(kind='crumbs', colour='#B5172D', light='#D0304A'), topping='raspberry', outer_drips=None),

    'caramel': dict(
        title='Caramel', ink='#3A1C08',
        sponge=dict(base='#EDCB8A', light='#F8E2B4', pore='#D9AE62', crust='#C98A45', crust_dark='#A86B30', shade='#D6A866'),
        bands=stack([(.3,) + SP, (.08, 'jam', '#B86A1C', '#9E5814'), (.3,) + SP]),
        coat=dict(style='full', kind='glaze', base='#D9933A', ramp=[(0.0, '#B8742A'), (0.55, '#C9852F'), (0.72, '#DC9A45')],
                  edge='#A6621C', rough=0.18, coat=0.6, coat_rough=0.07, sss=0.25, sss_radius=(1, .6, .25), band=0.095, drips='glaze'),
        pipe=None, pattern=dict(kind='drizzle', colour='#8A4A10'), topping='nut',
        outer_drips=dict(colour='#9C5713', light='#B86A1C')),
}
