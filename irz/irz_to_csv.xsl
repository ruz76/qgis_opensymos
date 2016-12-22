<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:math="http://exslt.org/math" extension-element-prefixes="math">
<xsl:output method="text"/>
<xsl:template match="/">
   <xsl:for-each select="//table[@class='list']/tr">
    <xsl:if test="td[2]/a/@href != ''">  
        <xsl:text>&#xa;</xsl:text>
        <xsl:value-of select="translate(td[2],';',' ')"/><xsl:text>;</xsl:text>	
        <xsl:value-of select="substring-after(td[2]/a/@href, 'id=')"/><xsl:text>;</xsl:text>	
    </xsl:if>
    <xsl:if test="td[3] != ''">  
        <xsl:value-of select="td[3]"/><xsl:text>;</xsl:text>	
    </xsl:if>
    <xsl:if test="td[4] != ''">  
        <xsl:value-of select="td[4]"/><xsl:text>;</xsl:text>	
    </xsl:if>    
   </xsl:for-each>
   <xsl:text>&#xa;</xsl:text>
</xsl:template>

</xsl:stylesheet>
