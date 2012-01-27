def disp_phrase( phrase, loc, font, screen ):
    s = font.render( phrase, True, ( 200, 200, 200 ) )
    sh = font.render( phrase, True, ( 50, 50, 50 ) )
    screen.blit( sh, ( loc[0]+1, loc[1]+1 ) )       # White
    screen.blit( s, loc )                           # A shadow

def toggle( var ):
    if ( var == True ):
        return False
    else:
        return True

def min_max( arr ):
    return min( arr ), max( arr )