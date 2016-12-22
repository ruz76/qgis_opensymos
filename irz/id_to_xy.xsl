<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:math="http://exslt.org/math" extension-element-prefixes="math">
<xsl:output method="text"/>
<xsl:template match="/">
   <xsl:for-each select="//p">
    <xsl:if test="substring-after(., 'JTSK:') != ''">  
        <xsl:value-of select="substring-before(substring-after(., 'JTSK:'), 'Sou')"/>
    </xsl:if> 
   </xsl:for-each>    
</xsl:template>

</xsl:stylesheet>
