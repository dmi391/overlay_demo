/*
 * Sample runtime overlay manager.
 */

typedef enum { FALSE, TRUE } boolean;

/* Entry Points: */

boolean OverlayLoad (unsigned int ovlyno);
boolean OverlayUnload (unsigned int ovlyno);
